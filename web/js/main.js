// The global module
var cta_train_rumbling = function(){
    var result = {};

    var far_left = "0%";
    var far_right = "100%";
    var transition_speed = 13000;

    var n_cars = 5;
    var car_height = 20;
    var car_width = car_height * (Math.sqrt(5) + 1);
    var car_spacing = car_height / 3;

    var train_height = car_height;
    var train_width = n_cars * (car_width + car_spacing);

    result.track_height = train_height;

    var cta_colors = {
      red: "#c60c30",
      blue: "#00a1de",
      brown: "#62361b",
      green: "#009b3a",
      orange: "#f9461c",
      purple: "#522398",
      pink: "#e27ea6",
      yellow: "#f9e300",
      grey: "#565a5c"
    };

    var whoosh = function(color, direction) {

      // print a poetic message to the console
      var word = "A ";
      if (color == 'orange') {
        word = "An ";
      }
      var message = word + color + " line train rumbles by at " + new Date();
      console.log(message);

      // set begin and end depending on direction of train
      var begin = far_left;
      var end = far_right;
      var track = "." + direction;
      if (direction === "southbound") {
        begin = far_right;
        end = far_left;
      }

      // create the train div
      var train = $('<div class="train"></div>');
      train.css({
        left: begin,
        height: train_height,
        width: train_width
      });
      _.each(_.range(n_cars), function (index) {
        var car = $('<div class="car"></div>');
        car.css({
          background: color,
          height: car_height,
          width: car_width,
          "margin-right": car_spacing

        });
        car.appendTo(train);
      });

      // animate it across the screen
      train.hide().appendTo($(track)).show().transition({
        left: end
      }, transition_speed, 'linear', function () {
        // console.log('woosh ended');
        train.remove();
      });
    };

    var milliseconds_between = function(t1, t2) {
      return t2.getTime() - t1.getTime();
    };

    var timeouts = []; // collection of all train schedule

    // Remove all previously scheduled train
    var clearAllTimeOuts = function(timeouts) {
        for (var i = 0; i < timeouts.length; i++) {
            clearTimeout(timeouts[i]);
        }
        //quick reset of the timer array you just cleared
        timeouts = [];
    }

    // schedule and trigger the passage of each train at the right time
    result.schedule_the_train_rumble = function(data) {
        var now = new Date();
        clearAllTimeOuts(timeouts) // Remove all previously scheduled train
        _.each(data, function (item) {
          var delay = milliseconds_between(now, new Date(item.pass_time));
          if (delay > 0) {
            var message = "scheduling " + item.direction + " " + item.color + " line train for " + new Date(item.pass_time);
            console.log(message);
            timeouts.push(window.setTimeout(whoosh, delay, item.color, item.direction));
          };
        });
    };

    return result

}();

$(document).ready(function () {

  // style the train tracks
  $('.tracks').css({
    "padding-bottom": cta_train_rumbling.track_height,
    height: cta_train_rumbling.track_height,
    "background-size": 3 * cta_train_rumbling.track_height / 10 + "px " + cta_train_rumbling.track_height + "px"
  });

  // trigger the passage of each train at the right time
  $.getJSON("./data/train-times.json", function(data) {
        return cta_train_rumbling.schedule_the_train_rumble(data)
  });

  // check for new schedule when the browser tab is in focus
  $(window).focus(function(){
    $.getJSON("./data/train-times.json", function(data) {
        return cta_train_rumbling.schedule_the_train_rumble(data)
    });
  });
});
