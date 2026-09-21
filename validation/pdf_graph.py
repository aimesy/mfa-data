"""Exact typed reachable PDF graph, including indirect arrays, aliases and cycles.

Only the selected page's /Parent edge is outside the extraction contract. Every
other reachable page/tree/destination/resource/annotation node is retained. Both
encoded and decoded stream bytes are pinned. Use joint_snapshot for acceptance;
separate-root snapshots are diagnostic only. Numbers retain exact source tokens
through parsing, cloning and writing; malformed numbers raise, never become zero. IDs are deterministic traversal
labels, not original object numbers. Review verification removes only the known
tail of the selected page annotation array, preserving that array's reference
identity, and compares the separately bound added annotation graph. No tolerance.
"""
from io import BytesIO
from decimal import Decimal
from contextlib import contextmanager
import logging,re,math
import importlib.metadata
from pypdf._utils import read_until_regex
from pypdf.errors import PdfReadError
import hashlib,json
from pypdf import PdfReader
from pypdf.generic import IndirectObject,DictionaryObject,ArrayObject,StreamObject,NullObject,BooleanObject,NumberObject,FloatObject,ByteStringObject,TextStringObject,NameObject

# Process-local reader hook: installed only within exact_pdf_numbers(). No runtime
# package files are modified. Float arithmetic is never the equality authority.
NUMERIC_TOKEN=re.compile(rb"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)\Z")
MAX_NUMERIC_TOKEN_BYTES=4096

def numeric_lexeme(value):
 if isinstance(value,ExactFloat):return value.exact_pdf_lexeme
 if isinstance(value,bytes):token=value
 elif isinstance(value,str):token=value.encode('ascii')
 elif isinstance(value,(NumberObject,int)) and not isinstance(value,bool):token=str(int(value)).encode('ascii')
 elif isinstance(value,Decimal):token=format(value,'f').encode('ascii')
 else:raise PdfReadError('Exact PDF number requires a source lexeme, not a floating approximation')
 if not 0<len(token)<=MAX_NUMERIC_TOKEN_BYTES or not NUMERIC_TOKEN.fullmatch(token):raise PdfReadError('Invalid or over-bound exact PDF numeric token')
 return token

def exact_tuple(token):
 # Decimal construction and tuple extraction are exact and context independent.
 sign,digits,exponent=Decimal(numeric_lexeme(token).decode('ascii')).as_tuple()
 digits=list(digits)
 if not any(digits):return [0,[0],0]
 while digits[-1]==0:digits.pop();exponent+=1
 return [sign,digits,exponent]

class ExactFloat(FloatObject):
 def __new__(cls,value):
  token=numeric_lexeme(value);approx=float(token)
  if not math.isfinite(approx):raise PdfReadError('PDF float exceeds finite runtime range; hold source')
  obj=float.__new__(cls,approx);obj.exact_pdf_lexeme=token;return obj
 def clone(self,pdf_dest,force_duplicate=False,ignore_fields=()):
  return self._reference_clone(ExactFloat(self.exact_pdf_lexeme),pdf_dest,force_duplicate)
 def myrepr(self):return self.exact_pdf_lexeme.decode('ascii')
 def __repr__(self):return self.myrepr()
 def __str__(self):return self.myrepr()
 def write_to_stream(self,stream,encryption_key=None):
  if encryption_key is not None:raise ValueError('Unsupported legacy encryption-key argument')
  stream.write(self.exact_pdf_lexeme)
 def hash_bin(self):return hash((self.__class__,self.exact_pdf_lexeme))

def read_exact_number(stream):
 parts=bytearray()
 while True:
  char=stream.read(1)
  if not char:break
  if char not in b'+-.0123456789':
   stream.seek(-1,1);break
  parts.extend(char)
  if len(parts)>MAX_NUMERIC_TOKEN_BYTES:raise PdfReadError('PDF numeric token exceeds explicit byte bound')
 token=numeric_lexeme(bytes(parts))
 if b'.' in token:return ExactFloat(token)
 return NumberObject(int(token))

@contextmanager
def exact_pdf_numbers():
 # This helper is used in an isolated synchronous research process, not across
 # threads. Keep the hook active for every lazy parse, graph walk and clone.
 if importlib.metadata.version('pypdf')!='6.16.2':raise RuntimeError('Unpinned pypdf parser runtime')
 saved=NumberObject.read_from_stream
 class Warnings(logging.Handler):
  def __init__(self):super().__init__(logging.WARNING);self.messages=[]
  def emit(self,record):self.messages.append(record.getMessage())
 handler=Warnings();logger=logging.getLogger('pypdf');logger.addHandler(handler)
 NumberObject.read_from_stream=staticmethod(read_exact_number)
 try:
  yield
  if handler.messages:raise PdfReadError('Unresolved PDF parser warnings: '+repr(handler.messages))
 finally:
  NumberObject.read_from_stream=staticmethod(saved);logger.removeHandler(handler)

def sha(b):return hashlib.sha256(b).hexdigest()
def deref(x):return x.get_object() if isinstance(x,IndirectObject) else x
class Graph:
 def __init__(self,page,overrides=None):
  ref=page.indirect_reference
  self.selected=(ref.idnum,ref.generation) if ref else None
  self.ids={};self.nodes={};self.overrides=overrides or {}
  self.reader=ref.pdf if ref else None;self.mupdf_document=None
 def decode_stream(self,x):
  filters=x.get('/Filter',[])
  names=[str(k) for k in filters] if isinstance(filters,ArrayObject) else [str(filters)]
  if '/JBIG2Decode' not in names:return x.get_data(),'pypdf-filter-decoding'
  import pymupdf as fitz
  import importlib.metadata
  if importlib.metadata.version('PyMuPDF')!='1.28.2':raise ValueError('Unpinned JBIG2 decoder runtime')
  ref=x.indirect_reference
  if not isinstance(ref,IndirectObject) or ref.pdf is not self.reader:raise ValueError('Unbound JBIG2 source reference')
  if str(x.get('/Subtype'))!='/Image' or x.get('/BitsPerComponent')!=1:raise ValueError('Unsupported JBIG2 stream role or bit depth')
  width=int(x['/Width']);height=int(x['/Height']);expected=((width+7)//8)*height
  if width<=0 or height<=0 or expected>64*1024*1024:raise ValueError('JBIG2 decoded size outside explicit bound')
  if self.mupdf_document is None:
   prior=fitz.TOOLS.mupdf_warnings(reset=True)
   if prior:raise ValueError('Prior unreviewed MuPDF warnings: '+prior)
   self.mupdf_document=fitz.open(stream=self.reader.stream.getvalue(),filetype='pdf')
  d=self.mupdf_document
  if d.xref_stream_raw(ref.idnum)!=x._data:raise ValueError('JBIG2 encoded source bytes disagree across parsers')
  decoded=d.xref_stream(ref.idnum)
  warnings=fitz.TOOLS.mupdf_warnings(reset=True)
  if warnings:raise ValueError('JBIG2 source decode warnings: '+warnings)
  if not isinstance(decoded,bytes) or len(decoded)!=expected:raise ValueError('JBIG2 packed bitmap length differs from exact width/height')
  return decoded,'PyMuPDF-1.28.2-xref_stream-JBIG2-packed-one-bit-rows'
 def __del__(self):
  d=getattr(self,'mupdf_document',None)
  if d is not None:d.close()
 def norm(self,x):
  if isinstance(x,IndirectObject):
   ident=(x.idnum,x.generation)
   if ident==self.selected:return {'selected_page_back_reference':True}
   if ident in self.ids:return {'ref':self.ids[ident]}
   key='n'+str(len(self.ids));self.ids[ident]=key;self.nodes[key]=None
   target=self.overrides[ident] if ident in self.overrides else x.get_object()
   if target is None:raise ValueError('Undefined original/reference object '+str(x.idnum)+' '+str(x.generation))
   self.nodes[key]=self.norm(target)
   return {'ref':key}
  if isinstance(x,StreamObject):
   decoded,method=self.decode_stream(x);encoded=x._data
   assert isinstance(encoded,bytes)
   return {'type':'stream','decoded_method':method,'dictionary':{str(k):self.norm(v) for k,v in sorted(x.items(),key=lambda a:str(a[0]))},'decoded_bytes':len(decoded),'decoded_sha256':sha(decoded),'encoded_bytes':len(encoded),'encoded_sha256':sha(encoded)}
  if isinstance(x,DictionaryObject):return {'type':'dictionary','entries':{str(k):self.norm(v) for k,v in sorted(x.items(),key=lambda a:str(a[0]))}}
  if isinstance(x,(ArrayObject,list,tuple)):return {'type':'array','items':[self.norm(a) for a in x]}
  if isinstance(x,NullObject) or x is None:return {'type':'null'}
  if isinstance(x,BooleanObject) or isinstance(x,bool):return {'type':'boolean','value':bool(x.value) if isinstance(x,BooleanObject) else x}
  if isinstance(x,ExactFloat):return {'type':'number','exact_decimal_tuple':exact_tuple(x.exact_pdf_lexeme)}
  if isinstance(x,(NumberObject,int,Decimal)):return {'type':'number','exact_decimal_tuple':exact_tuple(x)}
  if isinstance(x,(FloatObject,float)):raise PdfReadError('Unbound or rounded floating PDF number; exact parser context required')
  if isinstance(x,ByteStringObject) or isinstance(x,bytes):return {'type':'bytes','hex':bytes(x).hex()}
  if isinstance(x,NameObject):return {'type':'name','value':str(x)}
  if isinstance(x,(TextStringObject,str)):return {'type':'text','value':str(x)}
  raise TypeError('Unsupported PDF object '+type(x).__name__)
 def pack(self,roots):
  assert all(v is not None for v in self.nodes.values())
  return {'roots':roots,'nodes':self.nodes,'node_count':len(self.nodes)}
def snapshot(raw,page_index,annotation_limit=None,original_annots_present=None):
 reader=PdfReader(BytesIO(raw));p=reader.pages[page_index]
 present='/Annots' in p
 container=p.raw_get('/Annots') if present else None
 anns=list(deref(container)) if present else []
 assert annotation_limit is None or 0<=annotation_limit<=len(anns)
 if annotation_limit is not None:assert isinstance(original_annots_present,bool)
 original_present=present if annotation_limit is None else original_annots_present
 if original_present:assert present
 if not original_present:assert annotation_limit in [None,0]
 selected=anns if annotation_limit is None else anns[:annotation_limit]
 overrides={}
 if present and isinstance(container,IndirectObject) and annotation_limit is not None:
  overrides[(container.idnum,container.generation)]=ArrayObject(selected)
 g=Graph(p,overrides)
 entries={}
 for k,v in sorted(p.items(),key=lambda a:str(a[0])):
  k=str(k)
  if k=='/Parent':continue
  if k=='/Annots':
   if not original_present:continue
   if annotation_limit is not None and not isinstance(container,IndirectObject):v=ArrayObject(selected)
  entries[k]=g.norm(v)
 result=g.pack({'page':entries})
 result['original_annotation_count']=len(selected)
 result['original_annots_present']=original_present
 return result,reader
def annotation_graph(raw,page_index,annotation_index):
 reader=PdfReader(BytesIO(raw));p=reader.pages[page_index];anns=list(deref(p.get('/Annots',ArrayObject())))
 assert 0<=annotation_index<len(anns)
 g=Graph(p);root=g.norm(anns[annotation_index])
 return g.pack({'annotation':root})
def annotation_count(raw,page_index):
 reader=PdfReader(BytesIO(raw));p=reader.pages[page_index]
 return len(deref(p.get('/Annots',ArrayObject())))
def digest(x):return sha(json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode('utf-8'))

def catalog_snapshot(raw,page_index):
 reader=PdfReader(BytesIO(raw));page=reader.pages[page_index];g=Graph(page)
 # The newly added display page-tree edge is the only catalog exclusion.
 # All other catalog keys and their entire reachable reference graphs remain.
 roots={str(k):g.norm(v) for k,v in sorted(reader.root_object.items(),key=lambda a:str(a[0])) if str(k)!='/Pages'}
 return g.pack({'catalog_except_display_pages':roots}),reader


def joint_snapshot(raw,page_index,annotation_limit=None,original_annots_present=None):
 """One deterministic graph across both roots binds all cross-root aliases.

 The selected page Parent and display-catalog Pages edges are excluded only.
 All other reachable objects, including original page trees reached through
 catalog metadata, remain part of the graph. Only a prescribed annotation tail
 may be removed. Original missing, null and empty Annots remain distinct.
 """
 with exact_pdf_numbers():
  reader=PdfReader(BytesIO(raw));p=reader.pages[page_index]
  present='/Annots' in p;container=p.raw_get('/Annots') if present else None
  resolved=deref(container) if present else None
  if present and not isinstance(resolved,(ArrayObject,NullObject)):raise PdfReadError('Invalid or undefined serialized annotation container')
  anns=list(resolved) if isinstance(resolved,ArrayObject) else []
  if annotation_limit is not None:
   if not isinstance(annotation_limit,int) or isinstance(annotation_limit,bool) or not 0<=annotation_limit<=len(anns):raise ValueError('Invalid annotation tail bound')
   if not isinstance(original_annots_present,bool):raise ValueError('Original Annots presence must be bound')
  original_present=present if annotation_limit is None else original_annots_present
  if original_present and not present:raise ValueError('Original Annots removed')
  if not original_present and annotation_limit not in [None,0]:raise ValueError('Original annotation count inconsistent')
  selected=anns if annotation_limit is None else anns[:annotation_limit]
  overrides={}
  # Null originals require no appended squares under this generic contract:
  # conversion of null to an array needs a separately explicit restoration rule.
  if annotation_limit is not None and isinstance(resolved,NullObject) and selected:raise ValueError('Null annotation container cannot contain annotations')
  if present and isinstance(container,IndirectObject) and annotation_limit is not None and isinstance(resolved,ArrayObject):overrides[(container.idnum,container.generation)]=ArrayObject(selected)
  g=Graph(p,overrides);page={}
  for k,v in sorted(p.items(),key=lambda a:str(a[0])):
   k=str(k)
   if k=='/Parent':continue
   if k=='/Annots':
    if not original_present:continue
    if annotation_limit is not None and not isinstance(container,IndirectObject) and isinstance(resolved,ArrayObject):v=ArrayObject(selected)
   page[k]=g.norm(v)
  catalog={str(k):g.norm(v) for k,v in sorted(reader.root_object.items(),key=lambda a:str(a[0])) if str(k)!='/Pages'}
  result=g.pack({'page':page,'catalog_except_display_pages':catalog})
  result['original_annotation_count']=len(selected);result['original_annots_present']=original_present
  return result,reader

# Legacy individual-root utilities remain only to bind a named review annotation
# or supply diagnostics. They do not establish complete extraction equivalence.
_legacy_snapshot=snapshot
_legacy_catalog_snapshot=catalog_snapshot
_legacy_annotation_graph=annotation_graph
_legacy_annotation_count=annotation_count

def snapshot(*args,**kwargs):
 with exact_pdf_numbers():return _legacy_snapshot(*args,**kwargs)
def catalog_snapshot(*args,**kwargs):
 with exact_pdf_numbers():return _legacy_catalog_snapshot(*args,**kwargs)
def annotation_graph(*args,**kwargs):
 with exact_pdf_numbers():return _legacy_annotation_graph(*args,**kwargs)
def annotation_count(*args,**kwargs):
 with exact_pdf_numbers():return _legacy_annotation_count(*args,**kwargs)
