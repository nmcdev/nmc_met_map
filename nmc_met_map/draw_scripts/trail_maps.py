import matplotlib.pyplot as plt
import cartopy.io.img_tiles as cimgt
import cartopy.crs as ccrs
class TDT_img(cimgt.GoogleWTS):
    def _image_url(self, tile):
        x, y, z = tile
        url = 'https://webst01.is.autonavi.com/appmaptile?x=%s&y=%s&z=%s&style=6'% (x, y, z)
        return url
class TDT_ter(cimgt.GoogleWTS):
    def _image_url(self, tile):
        x, y, z = tile
        url = 'http://mt2.google.cn/vt/lyrs=p&scale=2&hl=zh-CN&gl=cn&x=%s&y=%s&z=%s'% (x, y, z)
        return url
class TDT(cimgt.GoogleWTS):
    def _image_url(self, tile):
        x, y, z = tile
        url = 'http://wprd01.is.autonavi.com/appmaptile?x=%s&y=%s&z=%s&lang=zh_cn&size=1&scl=1&style=7'% (x, y, z)
        return url
def make_map(projection=ccrs.PlateCarree()):
    #fig, ax = plt.subplots(figsize=(9, 13),subplot_kw=dict(projection=projection))

    plt.figure(figsize=(16,9))
    plotcrs = ccrs.Orthographic(central_longitude=70.,central_latitude=0)
    ax = plt.axes([0.01,0.1,.98,.84], projection=plotcrs)
    #gl = ax.gridlines(draw_labels=True)
    #gl.xlabels_top = gl.ylabels_right = False
    #gl.xformatter = LONGITUDE_FORMATTER
    #gl.yformatter = LATITUDE_FORMATTER
    #return fig, ax
    return ax
#extent = [60.0,140.8,5,50] 
#extent = [101.0,102.8,27.3,28.7] #
#request = TDT() #矢量图层
request = TDT_img() #卫星图像
#request = TDT_ter() #谷歌地形图
#fig, ax = make_map(projection=request.crs)
ax = make_map(projection=request.crs)
#ax.set_extent(extent)
ax.add_image(request, 3)# level=10 缩放等级 
plt.show()