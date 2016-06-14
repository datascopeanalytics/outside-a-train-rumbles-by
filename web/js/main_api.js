// This script won't work.
// Javascript/AJAX does not do cross domain call!!!

var CTATrainTracker = function () {
    this.api_key = '0618f22cc845471b99be936fac52f64d';
    this.base_url = 'http://lapi.transitchicago.com/api/1.0';
};

CTATrainTracker.prototype.arrival = function(map_id){
    var payload = {
        mapid: map_id,
        stpid: undefined,
        max: undefined,
        rt: undefined,
        key: this.api_key
    };

    $.get(this.base_url+'/ttarrivals.aspx', payload).done(function( data ) {
        alert( "Data Loaded: " + data );
        return data
    });

};

$(document).ready(function(){
    var newTrain = new CTATrainTracker();
    console.log(newTrain.arrival(40200));
});



