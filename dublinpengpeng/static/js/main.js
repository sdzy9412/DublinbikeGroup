// the basic functionality JS code
function initMap(){
    //callback function of google map API
    ROOT = window.location.origin;

    radius = 20, zoom = 14;
    var dublin_downtown = {
      lat:53.346763,
      lng:-6.2568436
    };

    //Set default map options
    var mapDefault = {
        center: dublin_downtown,
        zoom: 13,
        mapTypeId: google.maps.MapTypeId.ROADMAP
    };

    map = new google.maps.Map(document.getElementById('map'), mapDefault);

    //Initialize google map services, layers and markers variables
    var directionsService = new google.maps.DirectionsService();
    var directionsRenderer = new google.maps.DirectionsRenderer();

    var heatresult = [];
    var weight_point;

    var bikeLayer = new google.maps.BicyclingLayer();
    var trafficLayer = new google.maps.TrafficLayer();
    var heatLayer = new google.maps.visualization.HeatmapLayer({
        data: heatresult,
        map: map,
        radius: 15
    });

    //Set station markers as global variables
    var AllStationMarker = [];

    //Use setMap method to place and remove markers
    function setMapOnAll(map) {
        for (var i = 0; i < AllStationMarker.length; i++) {
            AllStationMarker[i].setMap(map);
        }
    }

    //Call setMapOnAll() function to remove marker from map, the marker information remain in the list
    function clearMarkers() {
        setMapOnAll(null);
    }

    //jQuery trigger the clicking button event
    //default button for default google map layer(hiding other layers)
    $('#default-b').click(function(){
        bikeLayer.setMap(null);
        trafficLayer.setMap(null);
        setMapOnAll(map);
        heatLayer.setMap(null);
        directionsRenderer.setMap(null);
    });

    //traffic button for traffic layer(hiding other layers)
    $('#traffic-b').click(function(){
        bikeLayer.setMap(null);
        trafficLayer.setMap(map);
        heatLayer.setMap(null);
        setMapOnAll(map);
        directionsRenderer.setMap(null);
    });

    //bike button for bike layer(hiding other layers)
    $('#bike-b').click(function(){
        bikeLayer.setMap(map);
        trafficLayer.setMap(null);
        heatLayer.setMap(null);
        setMapOnAll(map);
        directionsRenderer.setMap(null);
    });

    //heat button for bike stands heatmap(hiding other layers)
    $('#heat-b').click(function(){
        bikeLayer.setMap(null);
        trafficLayer.setMap(null);
        heatLayer.setMap(map);
        setMapOnAll(map);
        directionsRenderer.setMap(null)
    });

    /*
    $('#forecast_form').submit(function(event){
        console.log("successfully submit");
    });

    $('#forecast').click(function(){
        $('#forecast_form').submit();
    });
    */

    //ajax function to submit prediction form in POST method and draw charts for the data returned
    $(document).ready(function(){
        $('form').on('submit',function(event){
            var predict_pick_array = [];
            var predict_drop_array = [];
            $.ajax({
                data:{
                    pick: $('#pickupstation').val(),
                    pickdate: $('#pickdate').val(),
                    picktime: $('#picktime').val(),
                    drop: $('#dropoffstation').val(),
                    dropdate: $('#dropdate').val(),
                    droptime: $('#droptime').val()
                },
                type: "POST",
                url: '/predict'
            })
            .done(function(data){
                if("preresult" in data){
                    var results = data.preresult;
                    var pick_results = results[0];
                    var drop_results = results[1];
                    var weather_results = results[2];

                    //Get weather forecast information back and pass it to weather_bar function
                    pick_weather = weather_bar(weather_results[1]);
                    drop_weather = weather_bar(weather_results[4]);

                    //Set progress bar for weather forecast
                    document.getElementById("weatherforecast").innerHTML = "<div><p><strong>Bicycling suitability</strong></p></div><div><p>Start point: "+weather_results[1]+"</p></div><div class=\"progress border\" style=\"width:60%\">"+pick_weather+"</div><br><div><p>End point: "+weather_results[4]+"</p><div class=\"progress border\" style=\"width:60%\">"+drop_weather+"</div>";

                    //Construct prediction array for google chart
                    _.forEach(pick_results, function(pick_result){
                        predict_pick_array.push([new Date(pick_result[0]), pick_result[1]]);
                    })

                    _.forEach(drop_results, function(drop_result){
                        predict_drop_array.push([new Date(drop_result[0]), drop_result[1]]);
                    })

                    //Draw bar chart in the chart section
                    google.charts.load("current", {packages:['corechart', 'bar']});
                    google.setOnLoadCallback(function() { drawPredictChart(predict_pick_array, 'chart7_div', 'available bikes in pick up station in forecast'); });
                    google.setOnLoadCallback(function() { drawPredictChart(predict_drop_array, 'chart8_div', 'available bike stands in drop off station in forecast'); });

                }
            });

            event.preventDefault();
        });
    });


    //When sumbit button clicked in login mode, render direction between pickup and dropoff station
    $('#submitStation').click(function(){
            clearMarkers();
            bikeLayer.setMap(null);
            trafficLayer.setMap(null);
            heatLayer.setMap(null);
            var pickupMarker = document.getElementById("pickupstation");
            var dropoffMarker = document.getElementById("dropoffstation");
            //console.log(pickupMarker);
            var pickupMarkerValue = pickupMarker.options[pickupMarker.selectedIndex].value;
            var dropoffMarkerValue = dropoffMarker.options[dropoffMarker.selectedIndex].value;
            $.getJSON("/stations", function(data){
                if("stations" in data){
                    var stations = data.stations;
                    var origin, destionation;
                    var start_Station, end_Station;
                    _.forEach(stations, function(station){
                        if(pickupMarkerValue == station.number){
                            origin = new google.maps.LatLng(parseFloat(station.latitude), parseFloat(station.longitude));
                            start_Station = station.name;
                        }

                        if(dropoffMarkerValue == station.number){
                            destionation = new google.maps.LatLng(parseFloat(station.latitude), parseFloat(station.longitude));
                            end_Station = station.name;
                        }
                    })

                    var request = {
                        origin: origin,
                        destination: destionation,
                        travelMode: 'BICYCLING'
                    };

                    directionsService.route(request, function(response, status) {
                        if (status == 'OK') {
                        directionsRenderer.setDirections(response);
                        }
                    });
                    document.getElementById("solution_content").innerHTML = 'Start at station: '+start_Station+'. End at station: '+end_Station;
                    if (document.getElementById("profile-username").innerHTML == 'Visitor'){
                    }else{
                    solutonMap = new google.maps.Map(document.getElementById('solution_map'), mapDefault);

                    //render solution route map in the solution section
                    directionsRenderer.setMap(solutonMap);

                    //render solution panel instruction in the solution section
                    directionsRenderer.setPanel(document.getElementById('directionsPanel'));
                    }
                }

            });

            setMapOnAll(map);
            directionsRenderer.setMap(null);

    });

    //$('#default').click(function(){
    //    showAllStationMarkers();
    //});

    //Show all station marker with current dynamic information on the map
    function showAllStationMarkers(){
        var url_static = "/stations";
        var url_dynamic = "/available";
        var url_weather = "/weather";

        $.when(
            $.getJSON(url_static),
            $.getJSON(url_dynamic),
            $.getJSON(url_weather)
        ).done(function(data1, data2, data3){
            var parse1 = data1[0];
            var parse2 = data2[0];
            var parse3 = data3[0];
            //console.log(parse1);
            //console.log(parse2);
            if("stations" in parse1 && "available" in parse2 && "weather" in parse3){
                var stations = parse1.stations;
                var available = parse2.available;
                var weather = parse3.weather[0];
                _.forEach(stations, function(station){
                    //console.log('station', station.number);
                    _.forEach(available, function(avail){
                        //console.log('avail', avail.number);
                        if(station.number == avail.number){
                            var available_bikes = avail.available_bikes;
                            var available_bike_stands = avail.available_bike_stands;
                            var url;
                            //Present marker with different color based on the number of available bikes.
                            if(available_bikes <= 3){
                                url = "http://maps.google.com/mapfiles/ms/icons/red-dot.png";
                            }else if(available_bikes <= 10){
                                url = "http://maps.google.com/mapfiles/ms/icons/yellow-dot.png";
                            }else{
                                url = "http://maps.google.com/mapfiles/ms/icons/green-dot.png";
                            }

                            //initialize heatmap weight point option with the number of available bike stands
                            if(available_bike_stands > 25){
                                weight_point = 1;
                            }else{
                                weight_point = 0.2;
                            }

                            //Construct heatmap array
                            heatresult.push({
                                location: new google.maps.LatLng(parseFloat(station.latitude), parseFloat(station.longitude)),
                                weight: weight_point
                            });

                            var marker = new google.maps.Marker({
                                map: map,
                                position:{
                                    lat:parseFloat(station.latitude),
                                    lng:parseFloat(station.longitude)
                                },
                                icon:{
                                    url:url
                                }
                            });

                            //Get weather information and present it in weather section
                            document.getElementById("temp_temp").innerHTML = weather.temperature;
                            document.getElementById("temp_wind").innerHTML = weather.windSpeed;
                            document.getElementById("temp_humi").innerHTML = weather.humidity;
                            AllStationMarker.push(marker);

                            //Insert weather icon in the information window
                            var content = "<img src=\"" + weather.weatherIcon + ".png\" style=\"width: 40%\">" + "<p>Bike Station: "+station.name+"</p><p>Available bike stands: "+available_bike_stands+"</p><p>Available bikes: "+available_bikes+"</p>";
                            var infowindow = new google.maps.InfoWindow({maxWidth: 220});

                            //Add event listener to show information window when markers are clicked
                            google.maps.event.addListener(marker,'click', (function(marker,content,infowindow){
                                return function() {
                                    infowindow.setContent(content);
                                    infowindow.open(map,marker);
                                };
                            })(marker,content,infowindow));

                            //Add event listener to close information window when other places on map are clicked
                            google.maps.event.addListener(map, 'click', function () {
                                infowindow.close();
                            });

                        }
                    })


                })
                //console.log(AllStationMarker);
                setMapOnAll(map);
            }
        });
    }


    showAllStationMarkers();

    dropdownStationMenu();

    setDatetimeLimit();
}

//Drop down station selection list
function dropdownStationMenu(){
    var selectPickUpStation = "<select id='pickupstation' name ='pick'>";
    var selectDropOffStation = "<select id='dropoffstation' name ='drop'>";
    selectPickUpStation += "<option value=" + '0' + ">" + 'Select Pick Up Station:' + "</option>"
    selectDropOffStation += "<option value=" + '0' + ">" + 'Select Drop Off Station:' + "</option>"
    $.getJSON("/stations", function(data){
        if("stations" in data){
            var stations = data.stations;
            _.forEach(stations, function(station){
                selectPickUpStation += "<option value=\"" + station.number + "\">" + station.name + "</option>"
                selectDropOffStation += "<option value=\"" + station.number + "\">" + station.name + "</option>"
            })
            selectPickUpStation += "</select>";
            selectDropOffStation += "</select>";
        }

        document.getElementById("pickUpStation").innerHTML = selectPickUpStation;
        document.getElementById("dropOffStation").innerHTML = selectDropOffStation;
    });
}

//Draw charts specified by current time when submit button clicked
function onclickSubmit(){
    var currentDate = new Date();
    var currentTimestamp = currentDate.getTime();
    //console.log(currentTimestamp);
    var pickup = document.getElementById("pickupstation");
    var pickupValue = pickup.options[pickup.selectedIndex].value;

    var dropoff = document.getElementById("dropoffstation");
    var dropoffValue = dropoff.options[dropoff.selectedIndex].value;

    url_pickup = "/available/" + pickupValue;
    url_dropoff = "/available/" + dropoffValue;

    //console.log(url_pickup);

    $.when(
        $.getJSON(url_pickup),
        $.getJSON(url_dropoff)
    ).done(function(data1, data2){
        var parse1 = data1[0];
        var parse2 = data2[0];
        if("availableid" in parse1 && "availableid" in parse2){
            var pickupInfo = parse1.availableid;
            var dropoffInfo = parse2.availableid;
            var DailyArraypick = [];
            var DailyArraydrop = [];
            var WeeklyArraypick = [];
            var WeeklyArraydrop = [];
            var AverageArraypick = [];
            var AverageArraydrop = [];
            var total_0 = count_0 = total_1 = count_1 = total_2 = count_2 = total_3 = count_3 = total_4 = count_4 = total_5 = count_5 = total_6 = count_6 = 0;
            _.forEach(pickupInfo, function(pickupInfoElem){
                //Parse datetime string in javascript regular expression
                var dateRegexp = /(?<day>[0-9]{2})-(?<month>[a-zA-Z]{3})-(?<year>[0-9]{4})/;
                var timeRegexp = /(?<hour>[0-9]{2}):(?<minute>[0-9]{2}):(?<second>[0-9]{2})/;
                var pickupdatetime = pickupInfoElem.datetime;
                var pickupdate = pickupdatetime.match(dateRegexp).groups;
                var pickuptime = pickupdatetime.match(timeRegexp).groups;

                IntMonth = monthStringToInt(pickupdate.month);

                //Construct new timestamp object in javascript
                TimestampElem = toTimestamp(pickupdate.year, IntMonth, pickupdate.day, pickuptime.hour, pickuptime.minute, pickuptime.second);

                //Add daily array for pick up station
                if((currentTimestamp - TimestampElem)<86400000){
                    DailyArraypick.push([new Date(parseInt(pickupdate.year), parseInt(IntMonth)-1, parseInt(pickupdate.day), parseInt(pickuptime.hour), parseInt(pickuptime.minute), parseInt(pickuptime.second)),pickupInfoElem.available_bikes])
                }

                //Add weekly array for pick up station
                if((currentTimestamp - TimestampElem)<604800000){
                    WeeklyArraypick.push([new Date(parseInt(pickupdate.year), parseInt(IntMonth)-1, parseInt(pickupdate.day), parseInt(pickuptime.hour), parseInt(pickuptime.minute), parseInt(pickuptime.second)),pickupInfoElem.available_bike_stands])
                }

                //Determine day of the week for the timestamp
                switch (new Date(parseInt(pickupdate.year), parseInt(IntMonth)-1, parseInt(pickupdate.day), parseInt(pickuptime.hour), parseInt(pickuptime.minute), parseInt(pickuptime.second)).getDay()) {
                    case 0:
                      total_0 += pickupInfoElem.available_bikes;
                      count_0 += 1;
                      break;
                    case 1:
                      total_1 += pickupInfoElem.available_bikes;
                      count_1 += 1;
                      break;
                    case 2:
                      total_2 += pickupInfoElem.available_bikes;
                      count_2 += 1;
                      break;
                    case 3:
                      total_3 += pickupInfoElem.available_bikes;
                      count_3 += 1;
                      break;
                    case 4:
                      total_4 += pickupInfoElem.available_bikes;
                      count_4 += 1;
                      break;
                    case 5:
                      total_5 += pickupInfoElem.available_bikes;
                      count_5 += 1;
                      break;
                    case 6:
                      total_6 += pickupInfoElem.available_bikes;
                      count_6 += 1;
                  }

            })

            //Construct average weekly array for pick up station
            AverageArraypick = [
                ["Mon", total_1/count_1],
                ["Tue", total_2/count_2],
                ["Wed", total_3/count_3],
                ["Thu", total_4/count_4],
                ["Fri", total_5/count_5],
                ["Sat", total_6/count_6],
                ["Sun", total_0/count_0]
            ];

            //console.log(AverageArraypick);

            _.forEach(dropoffInfo, function(dropoffInfoElem){
                var dateRegexp = /(?<day>[0-9]{2})-(?<month>[a-zA-Z]{3})-(?<year>[0-9]{4})/;
                var timeRegexp = /(?<hour>[0-9]{2}):(?<minute>[0-9]{2}):(?<second>[0-9]{2})/;
                var dropoffdatetime = dropoffInfoElem.datetime;
                var dropoffdate = dropoffdatetime.match(dateRegexp).groups;
                var dropofftime = dropoffdatetime.match(timeRegexp).groups;

                IntMonth = monthStringToInt(dropoffdate.month);

                TimestampElem = toTimestamp(dropoffdate.year, IntMonth, dropoffdate.day, dropofftime.hour, dropofftime.minute, dropofftime.second);
                //console.log(TimestampElem);
                //Add daily array for drop off station
                if((currentTimestamp - TimestampElem)<86400000){
                    DailyArraydrop.push([new Date(parseInt(dropoffdate.year), parseInt(IntMonth)-1, parseInt(dropoffdate.day), parseInt(dropofftime.hour), parseInt(dropofftime.minute), parseInt(dropofftime.second)),dropoffInfoElem.available_bike_stands])
                }

                //Add weekly array for drop off station
                if((currentTimestamp - TimestampElem)<604800000){
                    WeeklyArraydrop.push([new Date(parseInt(dropoffdate.year), parseInt(IntMonth)-1, parseInt(dropoffdate.day), parseInt(dropofftime.hour), parseInt(dropofftime.minute), parseInt(dropofftime.second)),dropoffInfoElem.available_bike_stands])
                }

                //Determine day of the week for the timestamp
                switch (new Date(parseInt(dropoffdate.year), parseInt(IntMonth)-1, parseInt(dropoffdate.day), parseInt(dropofftime.hour), parseInt(dropofftime.minute), parseInt(dropofftime.second)).getDay()) {
                    case 0:
                      total_0 += dropoffInfoElem.available_bike_stands;
                      count_0 += 1;
                      break;
                    case 1:
                      total_1 += dropoffInfoElem.available_bike_stands;
                      count_1 += 1;
                      break;
                    case 2:
                      total_2 += dropoffInfoElem.available_bike_stands;
                      count_2 += 1;
                      break;
                    case 3:
                      total_3 += dropoffInfoElem.available_bike_stands;
                      count_3 += 1;
                      break;
                    case 4:
                      total_4 += dropoffInfoElem.available_bike_stands;
                      count_4 += 1;
                      break;
                    case 5:
                      total_5 += dropoffInfoElem.available_bike_stands;
                      count_5 += 1;
                      break;
                    case 6:
                      total_6 += dropoffInfoElem.available_bike_stands;
                      count_6 += 1;
                  }


            })

            //Construct average weekly array for drop off station
            AverageArraydrop = [
                ["Mon", total_1/count_1],
                ["Tue", total_2/count_2],
                ["Wed", total_3/count_3],
                ["Thu", total_4/count_4],
                ["Fri", total_5/count_5],
                ["Sat", total_6/count_6],
                ["Sun", total_0/count_0]
            ];

            //Draw bar charts and line charts separately
            google.charts.load("current", {packages:['corechart', 'bar']});
            google.setOnLoadCallback(function() { drawDailyChart(DailyArraypick, 'chart1_div', 'available bikes in pick up station in past 24 hours'); });
            google.setOnLoadCallback(function() { drawDailyChart(DailyArraydrop, 'chart2_div', 'available bike stands in drop off station in past 24 hours'); });

            google.charts.load("current", {packages:['line']});
            google.setOnLoadCallback(function() { drawWeeklyChart(WeeklyArraypick, 'chart3_div', 'available bikes in pick up station in past 7 days'); });
            google.setOnLoadCallback(function() { drawWeeklyChart(WeeklyArraydrop, 'chart4_div', 'available bike stands in drop off station in past 7 days'); });
            google.setOnLoadCallback(function() { drawAverageChart(AverageArraypick, 'chart5_div', 'available bikes in pick up station in average weekly'); });
            google.setOnLoadCallback(function() { drawAverageChart(AverageArraydrop, 'chart6_div', 'available bike stands in drop off station in average weekly'); });
        }
    });
}

function toTimestamp(year,month,day,hour,minute,second){
    // To get the timestamp in millisecond.
    // One day 86400 seconds.
    // One week 604800 seconds.
    var Timestamp = new Date(Date.UTC(year,month-1,day,hour,minute,second));
    return Timestamp.getTime()
}

function monthStringToInt(string){
    var num;
    switch (string) {
        case "Jan":
            num = 1;
            break;
        case "Feb":
            num = 2;
            break;
        case "Mar":
            num = 3;
            break;
        case "Apr":
            num = 4;
            break;
        case "May":
            num = 5;
            break;
        case "Jun":
            num = 6;
            break;
        case "Jul":
            num = 7;
            break;
        case "Aug":
            num = 8;
            break;
        case "Sep":
            num = 9;
            break;
        case "Oct":
            num = 10;
            break;
        case "Nov":
            num = 11;
            break;
        case "Dec":
            num = 12;
            break;
      }
    return num;
}

function drawDailyChart(DailyArray, div_place, titlename) {

    var data = new google.visualization.DataTable();
    data.addColumn('datetime');
    data.addColumn('number');

    data.addRows(DailyArray);

    var options = {
        title: titlename,
        chart: {
           height: 250,
           width: 500
            },
        vAxis: {
            viewWindowMode:'explicit',
            viewWindow: {
                min:0
            }
        },
        legend: {position: 'none'}
    };

    var chart = new google.charts.Bar(document.getElementById(div_place));

    chart.draw(data, google.charts.Bar.convertOptions(options));
}


function drawWeeklyChart(WeeklyArray, div_place, titlename) {

    var data = new google.visualization.DataTable();
    data.addColumn('datetime');
    data.addColumn('number');

    data.addRows(WeeklyArray);

    var options = {
        title: titlename,
        chart: {
            height: 250,
            width: 500
            },
        vAxis: {
            viewWindowMode:'explicit',
            viewWindow: {
                min:0
            }
        },
        legend: {position: 'none'}
    };

    var chart = new google.charts.Line(document.getElementById(div_place));

    chart.draw(data, google.charts.Line.convertOptions(options));

    //var chart = new google.visualization.LineChart(document.getElementById(div_place));

    //chart.draw(data, options);
}


function drawAverageChart(AverageArray, div_place, titlename){

    var data = new google.visualization.DataTable();
    data.addColumn('string');
    data.addColumn('number');

    data.addRows(AverageArray);

    var options = {
        title: titlename,
        chart: {
            height: 250,
            width: 500
            },
        vAxis: {
            viewWindowMode:'explicit',
            viewWindow: {
                min:0
            }
        },
        legend: {position: 'none'}
    };

    var chart = new google.charts.Line(document.getElementById(div_place));

    chart.draw(data, google.charts.Line.convertOptions(options));

    // var chart = new google.visualization.LineChart(document.getElementById(div_place));

    // chart.draw(data, options);
}

function drawPredictChart(PredictArray, div_place, titlename) {

    var data = new google.visualization.DataTable();
    data.addColumn('datetime');
    data.addColumn('number');

    data.addRows(PredictArray);

    var options = {
        title: titlename,
        chart: {
            height: 250,
            width: 500
            },
        vAxis: {
            viewWindowMode:'explicit',
            viewWindow: {
                min:0
            }
        },
        legend: {position: 'none'}
    };

    var chart = new google.charts.Bar(document.getElementById(div_place));

    chart.draw(data, google.charts.Bar.convertOptions(options));
}

//Set datetime limit for input calendar
function setDatetimeLimit(){
    var today = new Date();
    var dd = today.getDate();
    var mm = today.getMonth()+1; //January is 0!
    var yyyy = today.getFullYear();
    if(dd<10){
            dd='0'+dd
        }
    if(mm<10){
        mm='0'+mm
    }

    maxdd = dd + 4;
    min_date = yyyy+'-'+mm+'-'+dd;
    max_date = yyyy+'-'+mm+'-'+maxdd;
    if (document.getElementById("profile-username").innerHTML != 'Visitor'){
    document.getElementById("pickdate").setAttribute("min", min_date);
    document.getElementById("dropdate").setAttribute("min", min_date);
    document.getElementById("pickdate").setAttribute("max", max_date);
    document.getElementById("dropdate").setAttribute("max", max_date);
    }
}

//Convert weather string to progress bar insertion in html syntax
function weather_bar(weather){
    var output;
    switch(weather){
    case "Clear":
        output = "<div class=\"progress-bar\" style=\"width:90%\">90%</div>";
        break;
    case "Clouds":
        output = "<div class=\"progress-bar bg-secondary\" style=\"width:70%\">70%</div>";
        break;
    case "Drizzle":
        output = "<div class=\"progress-bar bg-warning\" style=\"width:50%\">50%</div>";
        break;
    case "Rain":
        output = "<div class=\"progress-bar bg-danger\" style=\"width:30%\">30%</div>";
        break;
    case "Mist":
        output = "<div class=\"progress-bar bg-dark\" style=\"width:10%\">10%</div>";

    }
    return output;
}





// the front-end UI JS code
!(function($) {
  "use strict";

  if ($('.typed').length) {
    var typed_strings = $(".typed").data('typed-items');
    typed_strings = typed_strings.split(',')
    new Typed('.typed', {
      strings: typed_strings,
      loop: true,
      typeSpeed: 100,
      backSpeed: 50,
      backDelay: 2000
    });
  }

  // Smooth scroll for the navigation menu and links with .scrollto classes
  // click X in nav bar, will fetch into the section with id X
  $(document).on('click', '.nav-menu a, .scrollto', function(e) {
    if (location.pathname.replace(/^\//, '') == this.pathname.replace(/^\//, '') && location.hostname == this.hostname) {
      e.preventDefault();
      var target = $(this.hash);
      if (target.length) {

        var scrollto = target.offset().top;

        $('html, body').animate({
          scrollTop: scrollto
        }, 1500, 'easeInOutExpo');
		  // for moble device
        if ($(this).parents('.nav-menu, .mobile-nav').length) {
          $('.nav-menu .active, .mobile-nav .active').removeClass('active');
          $(this).closest('li').addClass('active');
        }

        if ($('body').hasClass('mobile-nav-active')) {
          $('body').removeClass('mobile-nav-active');
          $('.mobile-nav-toggle i').toggleClass('bx bx-menu bx-window-close');
        }
        return false;
      }
    }
  });

  $(document).on('click', '.mobile-nav-toggle', function(e) {
    $('body').toggleClass('mobile-nav-active');
    $('.mobile-nav-toggle i').toggleClass('bx bx-menu bx-window-close');
  });

  $(document).click(function(e) {
    var container = $(".mobile-nav-toggle");
    if (!container.is(e.target) && container.has(e.target).length === 0) {
      if ($('body').hasClass('mobile-nav-active')) {
        $('body').removeClass('mobile-nav-active');
        $('.mobile-nav-toggle i').toggleClass('bx bx-menu bx-window-close');
      }
    }
  });

  // Navigation active state on scroll
  var nav_sections = $('section');
  var main_nav = $('.nav-menu, #mobile-nav');

  $(window).on('scroll', function() {
    var cur_pos = $(this).scrollTop() + 10;

    nav_sections.each(function() {
      var top = $(this).offset().top,
        bottom = top + $(this).outerHeight();

      if (cur_pos >= top && cur_pos <= bottom) {
        if (cur_pos <= bottom) {
          main_nav.find('li').removeClass('active');
        }
        main_nav.find('a[href="#' + $(this).attr('id') + '"]').parent('li').addClass('active');
      }
    });
  });

  // Back to top button
  $(window).scroll(function() {
    if ($(this).scrollTop() > 100) {
      $('.back-to-top').fadeIn('slow');
    } else {
      $('.back-to-top').fadeOut('slow');
    }
  });

  $('.back-to-top').click(function() {
    $('html, body').animate({
      scrollTop: 0
    }, 1500, 'easeInOutExpo');
    return false;
  });

})(jQuery);
