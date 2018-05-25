/**
 * Created by casm on 2018/4/26.
 */
var map = function () {
    var scaleLineControl = new ol.control.ScaleLine();
    //设置中心
    var coor = ol.proj.transform([104.293175, 35.7], 'EPSG:4326', 'EPSG:3857');
    var view = new ol.View({

        center: coor,
        zoom: 4,
        minZoom: 2,
        maxZoom: 17
    });
    var map = new ol.Map({
        //容器
        target: 'mapDiv',
        //图层
        layers: [
            new ol.layer.Tile({
                source: new ol.source.XYZ({
                    title: "天地图路网",
                    url: "http://t2.tianditu.com/DataServer?T=vec_w&x={x}&y={y}&l={z}"
                })
            }),
            new ol.layer.Tile({
                source: new ol.source.XYZ({
                    title: "天地图文字标注",
                    url: "http://t2.tianditu.com/DataServer?T=cva_w&x={x}&y={y}&l={z}"
                })
            }),

            /* new ol.layer.Tile({
             title: "天地图卫星影像",
             source: new ol.source.XYZ({
             url: "http://t3.tianditu.com/DataServer?T=img_w&x={x}&y={y}&l={z}"
             })
             }) */
        ],
        //视图中心和缩放等级
        view: view,
        //比例尺
        controls: ol.control.defaults({
            attributionOptions: {
                collapsible: false
            }
        }).extend([
            scaleLineControl
            //new ol.control.FullScreen()
        ])

    });
    ol.geom.Polygon()
}