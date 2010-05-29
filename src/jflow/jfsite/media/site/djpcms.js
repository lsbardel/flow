
(function($) {
    
    var dj = $.djpcms;

    /**
     * Decorator for Econometric ploting
     */
    dj.addDecorator({
        id:"econometric-plot",
        decorate: function($this,config) {
            if($.start_ecoplot) {
                var poptions = {
                        colors: ["#205497","#2D8633","#B84000","#d18b2c"],
                        grid: {hoverable: true, clickable: true, color: '#00264D', tickColor: '#A3A3A3'},
                        selection: {mode: 'xy', color: '#3399FF'},
                        lines: {show: true, lineWidth: 3},
                        shadowSize: 0
                };
                
                $.start_ecoplot($this,poptions);
            }
        }
    });
    
    
    

})(jQuery);
