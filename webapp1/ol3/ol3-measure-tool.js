var measure_tool = function(options) {
    var _this = this;

    /**
     * 测量的类型：测量距离、测量面积
     * @type {object}
     */
    var Measure_Type = {Distance: 'distance', Area: 'area'};

    /**
     * 测量距离的类型：在大地线上测量、在平面上测量
     * @type {object}
     */
    var Distance_Type = {Geodesic: 'geodesic', Planar: 'planar'};

    /**
     * 测量工具是否被初始化
     * @type {boolean}
     */
    var isReady = true;

    /**
     * 测量工具选项.
     * @type {object}
     */
    var _options = options || {};
    if(!_options["map"] ||
        !_options["map"] instanceof ol.Map) {
        isReady = false;
    }
    if(!_options["type"] ||
        (_options["type"] !=  Measure_Type.Distance &&
        _options["type"] !=  Measure_Type.Area)){
        _options["type"] = Measure_Type.Distance;
    }
    if(!_options["distance"] ||
        (_options["distance"] !=  Distance_Type.Geodesic &&
        _options["distance"] !=  Distance_Type.Planar)){
        _options["distance"] = Distance_Type.Planar;
    }

    if(!isReady) return;

    /**
     * 显示测量提示信息的元素
     * @type {Element}
     */
    var helpTooltipElement;

    /**
     * 显示工具提示信息的叠加对象
     * @type {ol.Overlay}
     */
    var helpTooltip;

    /**
     * 显示测量结果信息的元素
     * @type {Element}
     */
    var measureTooltipElement;

    /**
     * 显示测量结果信息的叠加对象
     * @type {ol.Overlay}
     */
    var measureTooltip;

    /**
     * 测量开始时的提示信息
     * @type {string}
     */
    var startMeasureMsg = '单击开始测量';

    /**
     * 测量时的提示信息
     * @type {string}
     */
    var continueMeasureMsg = '单击继续，双击结束';

    /**
     * 测量图形
     * @type {ol.Collection}
     */
    var features = new ol.Collection();

    /**
     * 测量图形数据源
     * @type {ol.source.Vector}
     */
    var featureSource = new ol.source.Vector({features: features});

    /**
     * 测量图形图层
     * @type {ol.layer.Vector}
     */
    var featureLayer = new ol.layer.Vector({
        source: featureSource,
        style: [
            new ol.style.Style({
                fill: new ol.style.Fill({
                    color: [255,243,164, 0.3]
                }),
                stroke: new ol.style.Stroke({
                    color: [255, 102, 102, 1],
                    width: 2
                })
            }),
            new ol.style.Style({
                image: new ol.style.Circle({
                    radius: 4,
                    stroke: new ol.style.Stroke({
                        color: [255, 102, 102, 1],
                        width: 2
                    }),
                    fill: new ol.style.Fill({
                        color: [255, 255, 255, 1]
                    })
                }),
                geometry: function (feature) {
                    var coordinates = _options["type"] == Measure_Type.Distance ? feature.getGeometry().getCoordinates() : feature.getGeometry().getCoordinates()[0];
                    return new ol.geom.MultiPoint(coordinates);
                }
            })
        ]
    });

    featureLayer.setZIndex(10001);
    _options["map"].addLayer(featureLayer);

    /**
     * 测量图形绘制工具
     * @type {ol.interaction.Draw}
     */
    var drawTool = new ol.interaction.Draw({
        features: features,
        type: (_options["type"] == Measure_Type.Distance ? 'LineString' : 'Polygon'),
        style: new ol.style.Style({
            fill: new ol.style.Fill({
                color: [255,243,164, 0.3]
            }),
            stroke: new ol.style.Stroke({
                color: [255, 102, 102, 1],
                lineDash: [5, 5],
                width: 2
            }),
            image: new ol.style.Circle({
                radius: 4,
                stroke: new ol.style.Stroke({
                    color: [255, 102, 102, 1],
                    width: 2
                }),
                fill: new ol.style.Fill({
                    color: [255, 255, 255, 1]
                })
            })
        })
    });

    /**
     * 当前绘制的图形要素
     * @type {ol.geom.Geometry}
     */
    var sketchFeature;

    /**
     * 绘制图形事件的监听函数
     * @type {function}
     */
    var drawListener;

    /**
     * wgs84椭球
     * @type {ol.Sphere}
     */
    var wgs84Sphere = new ol.Sphere(6378137);

    /**
     * 绘制工具的开始绘制事件函数
     * @param {ol.MapBrowserEvent} evt 地图事件对象
     */
    var postDrawStart = function(evt) {
        //工具未初始化完成或测量工具未激活时退出
        if(!isReady || !drawTool.getActive()) return;
        // console.log(_options['map'].getInteractions());
        // console.log(_options['map'].getInteractions().getKeys());
        // _options['map'].getInteractions().get('doubleClickZoom').setActive(false);
        //禁用地图双击放大事件
        _options['map'].getInteractions().getArray()[1].setActive(false);
        /**
         * 创建测量提示信息元素
         */
        createMeasureTooltip();

        sketchFeature = evt.feature;

        /** @type {ol.Coordinate|undefined} */
        var tooltipCoord = evt.coordinate;

        drawListener = sketchFeature.getGeometry().on('change', function (evt) {
            var geom = evt.target;
            var output;
            if (geom instanceof ol.geom.Polygon) {
                output = formatArea(geom);
                tooltipCoord = geom.getInteriorPoint().getCoordinates();
            } else if (geom instanceof ol.geom.LineString) {
                output = formatLength(geom);
                tooltipCoord = geom.getLastCoordinate();
            }

            if(!measureTooltipElement){
                createMeasureTooltip();
            }
            measureTooltipElement.innerHTML = output;
            measureTooltip.setPosition(tooltipCoord);
        });
    }

    /**
     * 绘制工具的完成绘制事件函数
     * @param {ol.MapBrowserEvent} evt 地图事件对象
     */
    var postDrawEnd = function(evt) {
        //工具未初始化完成或测量工具未激活时退出
        if(!isReady || !drawTool.getActive()) return;

        measureTooltipElement.className = 'tooltips tooltip-static';
        measureTooltip.setOffset([0, -7]);
        sketchFeature["measureTooltip"] = measureTooltip;

        sketchFeature = null;
        measureTooltipElement = null;
        ol.Observable.unByKey(drawListener);

        helpTooltip.setPosition(undefined);
        $(helpTooltipElement).addClass('hidden');

        _this.setActive(false);

    }

    /**
     * 鼠标移动事件函数
     * @param {ol.MapBrowserEvent} evt 地图事件对象
     */
    var postPointerMove = function(evt) {
        //工具未初始化完成或测量工具未激活时退出
        if(!isReady || !drawTool.getActive()) return;

        //拖动中
        if (evt.dragging) return;

        //工具提示信息
        var helpMsg = startMeasureMsg;

        if (sketchFeature) {
            var geom = (sketchFeature.getGeometry());
            if (geom instanceof ol.geom.Polygon) {
                helpMsg = continueMeasureMsg;
            } else if (geom instanceof ol.geom.LineString) {
                helpMsg = continueMeasureMsg;
            }
        }

        helpTooltipElement.innerHTML = helpMsg;
        helpTooltip.setPosition(evt.coordinate);

        $(helpTooltipElement).removeClass('hidden');
    }

    /**
     * 鼠标移出地图视图事件函数
     * @param {ol.MapBrowserEvent} evt 地图事件对象
     */
    var postMouseOut = function () {
        $(helpTooltipElement).addClass('hidden');
    }

    /**
     * 创建测量提示信息元素
     */
    var createHelpTooltip = function() {
        if (helpTooltipElement) {
            helpTooltipElement.parentNode.removeChild(helpTooltipElement);
        }

        helpTooltipElement = document.createElement('div');
        helpTooltipElement.className = 'tooltips hidden';

        helpTooltip = new ol.Overlay({
            element: helpTooltipElement,
            offset: [15, 0],
            positioning: 'center-left'
        });

        _options["map"].addOverlay(helpTooltip);
    }

    /**
     * 创建测量结果信息元素
     */
    var createMeasureTooltip = function() {
        if (measureTooltipElement) {
            measureTooltipElement.parentNode.removeChild(measureTooltipElement);
        }

        measureTooltipElement = document.createElement('div');
        measureTooltipElement.className = 'tooltips tooltip-measure';

        measureTooltip = new ol.Overlay({
            element: measureTooltipElement,
            offset: [0, -15],
            positioning: 'bottom-center'
        });

        _options["map"].addOverlay(measureTooltip);

        return measureTooltip;
    }

    /**
     * 格式化测量长度
     * @param {ol.geom.LineString} line
     * @return {string}
     */
    var formatLength = function(line) {
        var length;
        if(_options["distance"] == Distance_Type.Geodesic) {
            var coordinates = line.getCoordinates();
            length = 0;

            var sourceProj = _options["map"].getView().getProjection();
            for (var i = 0, ii = coordinates.length - 1; i < ii; ++i) {
                var c1 = ol.proj.transform(coordinates[i], sourceProj, 'EPSG:4326');
                var c2 = ol.proj.transform(coordinates[i + 1], sourceProj, 'EPSG:4326');

                length += wgs84Sphere.haversineDistance(c1, c2);
            }
        } else {
            length = Math.round(line.getLength() * 100) / 100;
        }

        var output;
        if (length > 100) {
            output = (Math.round(length / 1000 * 100) / 100) + "公里";
        } else {
            output = (Math.round(length * 100) / 100) + "米";
        }

        return output;
    }

    /**
     * 格式化测量面积
     * @param {ol.geom.Polygon} polygon
     * @return {string}
     */
    var formatArea = function(polygon) {
        var area;
        if(_options["distance"] == Distance_Type.Geodesic) {
            var sourceProj = _options["map"].getView().getProjection();
            var geom = polygon.clone().transform(sourceProj, 'EPSG:4326');
            var coordinates = geom.getLinearRing(0).getCoordinates();
            area = Math.abs(wgs84Sphere.geodesicArea(coordinates));
        } else {
            area = polygon.getArea();
        }

        var output;
        if (area > 10000) {
            output = (Math.round(area / 1000000 * 100) / 100) + "平方公里";
        } else {
            output = (Math.round(area * 100) / 100) + "平方米";
        }

        return output;
    }

    /**
     * 设置测量工具的激活状态
     * @param {boolean} active
     */
    this.setActive = function(active){
        //工具未初始化完成时退出
        if(!isReady) return;

        if(active){

            drawTool.setActive(true);

            //注册鼠标移动事件
            _options["map"].on('pointermove', postPointerMove);

            //注册绘制工具的开始绘制事件函数
            drawTool.on('drawstart', postDrawStart);

            //注册绘制工具的结束绘制事件函数
            drawTool.on('drawend', postDrawEnd);

            //注册鼠标移出地图视图事件函数
            $(_options["map"].getViewport()).on('mouseout', postMouseOut);
        }else{

            drawTool.setActive(false);

            //取消鼠标移动事件函数的注册
            _options["map"].un('pointermove', postPointerMove);

            //取消开始绘制事件函数的注册
            drawTool.un('drawstart', postDrawStart);

            //取消结束绘制事件函数的注册
            drawTool.un('drawend', postDrawEnd);

            //取消鼠标移出地图视图事件函数的注册
            $(_options["map"].getViewport()).off('mouseout', postMouseOut);

            // setTimeout("villageMap.setInfoToolActive(true);", 300);

            //测量完成后，延迟打开地图双击放大事件，以防双击结束测量时放大地图
            setTimeout(function () {
                _options['map'].getInteractions().getArray()[1].setActive(true);
            }, 300);

        }
    };

    /**
     * 清除测量图形
     */
    this.clearMeasures = function () {
        helpTooltip.setPosition(undefined);
        $(helpTooltipElement).addClass('hidden');

        var fea;
        var feaCount = features.getLength();
        for(var i = 0; i < feaCount; i++){
            fea = features.item(i);

            if(fea){
                _options["map"].removeOverlay(fea["measureTooltip"]);
            }
        }

        features.clear();
    }

    /**
     * 创建测量提示信息元素
     */
    createHelpTooltip();

    //默认不激活工具
    _this.setActive(false);

    _options["map"].addInteraction(drawTool);
}
