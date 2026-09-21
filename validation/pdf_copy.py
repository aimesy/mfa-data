"""Clone exact indirect aliases without content deduplication.

Caller must hold pinned exact_pdf_numbers() across reader construction, lazy
parsing, copying, writing and joint verification. This creates derivatives only.
"""
from pypdf import PdfWriter,PageObject
from pypdf.generic import IndirectObject,DictionaryObject,ArrayObject,StreamObject,NullObject,BooleanObject,NumberObject,FloatObject,ByteStringObject,TextStringObject,NameObject

def clone_selected(reader,index):
 selected_source=reader.pages[index]
 writer=PdfWriter();memo={}
 def transfer(value):
  if isinstance(value,IndirectObject):
   key=(id(value.pdf),value.idnum,value.generation)
   if key in memo:return memo[key]
   ref=writer._add_object(NullObject());memo[key]=ref
   target=value.get_object()
   if target is None:raise ValueError('Undefined source object during typed copy')
   copied=transfer(target);writer._objects[ref.idnum-1]=copied;copied.indirect_reference=ref
   return ref
  if isinstance(value,StreamObject):
   copied=type(value)()
   if not isinstance(value._data,bytes):raise TypeError('Unbound encoded stream bytes')
   copied._data=value._data
   for key,item in value.items():copied[NameObject(str(key))]=transfer(item)
   return copied
  if isinstance(value,DictionaryObject):
   copied=PageObject(writer) if isinstance(value,PageObject) or value.get('/Type')=='/Page' else DictionaryObject()
   for key,item in value.items():copied[NameObject(str(key))]=transfer(item)
   return copied
  if isinstance(value,ArrayObject):return ArrayObject([transfer(item) for item in value])
  if isinstance(value,NullObject):return NullObject()
  if isinstance(value,BooleanObject):return BooleanObject(value.value)
  if isinstance(value,NumberObject):return NumberObject(int(value))
  if isinstance(value,FloatObject):
   token=getattr(value,'exact_pdf_lexeme',None)
   if not isinstance(token,bytes):raise TypeError('Rounded/unbound source float forbidden')
   return type(value)(token)
  if isinstance(value,NameObject):return NameObject(str(value))
  if isinstance(value,ByteStringObject):return ByteStringObject(bytes(value))
  if isinstance(value,TextStringObject):
   copied=TextStringObject(str(value))
   for field in ('_original_bytes','autodetect_pdfdocencoding','autodetect_utf16','utf16_bom'):
    if hasattr(value,field):setattr(copied,field,getattr(value,field))
   return copied
  raise TypeError('Unsupported typed source object '+type(value).__name__)
 original_catalog_ref=transfer(reader.trailer.raw_get('/Root'))
 original_catalog=original_catalog_ref.get_object()
 selected_ref=transfer(selected_source.indirect_reference);selected=selected_ref.get_object()
 display=DictionaryObject(dict(original_catalog.items()))
 writer._root_object=writer._add_object(display).get_object()
 tree=DictionaryObject({NameObject('/Type'):NameObject('/Pages'),NameObject('/Count'):NumberObject(1),NameObject('/Kids'):ArrayObject([selected_ref])})
 tree_ref=writer._add_object(tree);writer._root_object[NameObject('/Pages')]=tree_ref;writer._pages=tree_ref
 selected[NameObject('/Parent')]=tree_ref;writer.flattened_pages=[selected]
 return writer
