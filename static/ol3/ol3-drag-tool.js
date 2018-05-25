/**
 * Define a namespace for the application.
 */
var drag_tool = {};


/**
 * @constructor
 * @extends {ol.interaction.Pointer}
 */
drag_tool.Drag = function() {

    ol.interaction.Pointer.call(this, {
        handleDownEvent: drag_tool.Drag.prototype.handleDownEvent,
        handleDragEvent: drag_tool.Drag.prototype.handleDragEvent,
        handleMoveEvent: drag_tool.Drag.prototype.handleMoveEvent,
        handleUpEvent: drag_tool.Drag.prototype.handleUpEvent
    });

    /**
     * @type {ol.Pixel}
     * @private
     */
    this.coordinate_ = null;

    /**
     * @type {string|undefined}
     * @private
     */
    this.cursor_ = 'pointer';

    /**
     * @type {ol.Feature}
     * @private
     */
    this.feature_ = null;

    /**
     * @type {string|undefined}
     * @private
     */
    this.previousCursor_ = undefined;

};
ol.inherits(drag_tool.Drag, ol.interaction.Pointer);


/**
 * @param {ol.MapBrowserEvent} evt Map browser event.
 * @return {boolean} `true` to start the drag sequence.
 */
drag_tool.Drag.prototype.handleDownEvent = function(evt) {
    var map = evt.map;

    var feature = map.forEachFeatureAtPixel(evt.pixel,
        function(feature) {
            return feature;
        });

    if (feature) {
        this.coordinate_ = evt.coordinate;
        this.feature_ = feature;
    }

    return !!feature;
};


/**
 * @param {ol.MapBrowserEvent} evt Map browser event.
 */
drag_tool.Drag.prototype.handleDragEvent = function(evt) {
    var deltaX = evt.coordinate[0] - this.coordinate_[0];
    var deltaY = evt.coordinate[1] - this.coordinate_[1];

    var geometry = /** @type {ol.geom.SimpleGeometry} */
        (this.feature_.getGeometry());
    geometry.translate(deltaX, deltaY);

    this.coordinate_[0] = evt.coordinate[0];
    this.coordinate_[1] = evt.coordinate[1];
};


/**
 * @param {ol.MapBrowserEvent} evt Event.
 */
drag_tool.Drag.prototype.handleMoveEvent = function(evt) {
    if (this.cursor_) {
        var map = evt.map;
        var feature = map.forEachFeatureAtPixel(evt.pixel,
            function(feature) {
                return feature;
            });
        var element = evt.map.getTargetElement();
        if (feature) {
            if (element.style.cursor != this.cursor_) {
                this.previousCursor_ = element.style.cursor;
                element.style.cursor = this.cursor_;
            }
        } else if (this.previousCursor_ !== undefined) {
            element.style.cursor = this.previousCursor_;
            this.previousCursor_ = undefined;
        }
    }
};


/**
 * @return {boolean} `false` to stop the drag sequence.
 */
drag_tool.Drag.prototype.handleUpEvent = function() {
    // 返回拖拽feature和coordinate
    if (this.onDragComplete != null) {
        this.onDragComplete(this.feature_, this.coordinate_);
    }
    this.coordinate_ = null;
    this.feature_ = null;
    return false;
};

/**
 * 拖拽完成回调函数
 * @type {null}
 */
drag_tool.Drag.prototype.onDragComplete = null;
