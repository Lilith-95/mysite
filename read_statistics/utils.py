from django.contrib.contenttypes.models import ContentType
from .models import ReadNum
def read_statistics_once_read(request, obj):	
	ct = ContentType.objects.get_for_model(obj) # 获取模型类或模型的实例
	key = "%s_%s_read" % (ct.model, obj.pk)
	if not request.COOKIES.get(key):
	        if ReadNum.objects.filter(content_type=ct, object_id=obj.pk).count():
	            # 存在记录
	            readnum = ReadNum.objects.get(content_type=ct, object_id=obj.pk)
	        else:
	            # 不存在对应记录
	            readnum = ReadNum(content_type=ct, object_id=obj.pk)
	        readnum.read_num += 1 # read_num是ReadNum的属性
	        readnum.save()  
	return key  