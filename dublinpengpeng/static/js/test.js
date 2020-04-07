function initMap(){

    ROOT = window.location.origin;

    radius = 20, zoom = 14;
    var dublin_downtown = {
      lat:53.346763,
      lng:-6.2568436
    };

    var mapDefault = {
        center: dublin_downtown,
        zoom: 13,
        mapTypeId: google.maps.MapTypeId.ROADMAP
    };

    map = new google.maps.Map(document.getElementById('map'), mapDefault);

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

    var AllStationMarker = [];

    function setMapOnAll(map) {
        for (var i = 0; i < AllStationMarker.length; i++) {
            AllStationMarker[i].setMap(map);
        }
    }

    function clearMarkers() {
        setMapOnAll(null);
        console.log(AllStationMarker);
    }

    $('#default-b').click(function(){
        bikeLayer.setMap(null);
        trafficLayer.setMap(null);
        setMapOnAll(map);
        heatLayer.setMap(null);
        directionsRenderer.setMap(null);
    });

    $('#traffic-b').click(function(){
        bikeLayer.setMap(null);
        trafficLayer.setMap(map);
        heatLayer.setMap(null);
        setMapOnAll(map);
        directionsRenderer.setMap(null);
    });

    $('#bike-b').click(function(){
        bikeLayer.setMap(map);
        trafficLayer.setMap(null);
        heatLayer.setMap(null);
        setMapOnAll(map);
        directionsRenderer.setMap(null);
    });

    $('#heat-b').click(function(){
        bikeLayer.setMap(null);
        trafficLayer.setMap(null);
        heatLayer.setMap(map);
        setMapOnAll(map);
        directionsRenderer.setMap(null)
    });

    $('#submitStation').click(function(){
        if($("#route").is(":checked")){
            clearMarkers();
            bikeLayer.setMap(null);
            trafficLayer.setMap(null);
            heatLayer.setMap(null);
            var pickupMarker = document.getElementById("pickupstation");
            var dropoffMarker = document.getElementById("dropoffstation");
            console.log(pickupMarker);
            var pickupMarkerValue = pickupMarker.options[pickupMarker.selectedIndex].value;
            var dropoffMarkerValue = dropoffMarker.options[dropoffMarker.selectedIndex].value;
            $.getJSON("http://localhost:5000/stations", function(data){
                if("stations" in data){
                    var stations = data.stations;
                    var origin, destionation;
                    _.forEach(stations, function(station){
                        if(pickupMarkerValue == station.number){
                            origin = new google.maps.LatLng(parseFloat(station.latitude), parseFloat(station.longitude));
                        }

                        if(dropoffMarkerValue == station.number){
                            destionation = new google.maps.LatLng(parseFloat(station.latitude), parseFloat(station.longitude));
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

                    directionsRenderer.setMap(map);

                }

            });
        }else{
            setMapOnAll(map);
            directionsRenderer.setMap(null);
        }
    });

    //$('#default').click(function(){
    //    showAllStationMarkers();
    //});

    function showAllStationMarkers(){
        var url_static = "http://localhost:5000/stations";
        var url_dynamic = "http://localhost:5000/available";
        var url_weather = "http://localhost:5000/weather";

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
                            if(available_bikes <= 3){
                                url = "http://maps.google.com/mapfiles/ms/icons/red-dot.png";
                            }else if(available_bikes <= 10){
                                url = "http://maps.google.com/mapfiles/ms/icons/yellow-dot.png";
                            }else{
                                url = "http://maps.google.com/mapfiles/ms/icons/green-dot.png";
                            }

                            if(available_bike_stands > 25){
                                weight_point = 1;
                            }else{
                                weight_point = 0.2;
                            }

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

                            AllStationMarker.push(marker);
                            console.log(weather.weatherIcon);
                            var content = "<img src=\"" + weather.weatherIcon + ".png\" style=\"width: 40%\">" + "<p>Bike Station: "+station.name+"</p><p>Available bike stands: "+available_bike_stands+"</p><p>Available bikes: "+available_bikes+"</p>";
                            var infowindow = new google.maps.InfoWindow({maxWidth: 220});


                            google.maps.event.addListener(marker,'click', (function(marker,content,infowindow){
                                return function() {
                                    infowindow.setContent(content);
                                    infowindow.open(map,marker);
                                };
                            })(marker,content,infowindow));

                            google.maps.event.addListener(map, 'click', function () {
                                infowindow.close();
                            });

                        }
                    })


                })
                console.log(AllStationMarker);
                setMapOnAll(map);
            }
        });
    }


    showAllStationMarkers();

    dropdownStationMenu();
}



function dropdownStationMenu(){
    var selectPickUpStation = "<select id='pickupstation' name ='pick'>";
    var selectDropOffStation = "<select id='dropoffstation' name ='drop'>";
    selectPickUpStation += "<option value=" + '0' + ">" + 'Select Pick Up Station:' + "</option>"
    selectDropOffStation += "<option value=" + '0' + ">" + 'Select Drop Off Station:' + "</option>"
    $.getJSON("http://localhost:5000/stations", function(data){
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

function onclickSubmit(){
    var currentDate = new Date();
    var currentTimestamp = currentDate.getTime()/1000;
    //console.log(currentTimestamp);
    var pickup = document.getElementById("pickupstation");
    var pickupValue = pickup.options[pickup.selectedIndex].value;

    var dropoff = document.getElementById("dropoffstation");
    var dropoffValue = dropoff.options[dropoff.selectedIndex].value;

    url_pickup = "http://localhost:5000/available/" + pickupValue;
    url_dropoff = "http://localhost:5000/available/" + dropoffValue;

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
            _.forEach(pickupInfo, function(pickupInfoElem){
                var dateRegexp = /(?<day>[0-9]{2})-(?<month>[a-zA-Z]{3})-(?<year>[0-9]{4})/;
                var timeRegexp = /(?<hour>[0-9]{2}):(?<minute>[0-9]{2}):(?<second>[0-9]{2})/;
                var pickupdatetime = pickupInfoElem.datetime;
                var pickupdate = pickupdatetime.match(dateRegexp).groups;
                var pickuptime = pickupdatetime.match(timeRegexp).groups;

                IntMonth = monthStringToInt(pickupdate.month);

                TimestampElem = toTimestamp(pickupdate.year, IntMonth, pickupdate.day, pickuptime.hour, pickuptime.minute, pickuptime.second);
                //console.log(TimestampElem);
                if((currentTimestamp - TimestampElem)<86400){
                    DailyArraypick.push([new Date(parseInt(pickupdate.year), parseInt(IntMonth)-1, parseInt(pickupdate.day), parseInt(pickuptime.hour), parseInt(pickuptime.minute), parseInt(pickuptime.second)),pickupInfoElem.available_bikes])
                }

                if((currentTimestamp - TimestampElem)<604800){
                    WeeklyArraypick.push([new Date(parseInt(pickupdate.year), parseInt(IntMonth)-1, parseInt(pickupdate.day), parseInt(pickuptime.hour), parseInt(pickuptime.minute), parseInt(pickuptime.second)),pickupInfoElem.available_bike_stands])
                }

            })

            _.forEach(dropoffInfo, function(dropoffInfoElem){
                var dateRegexp = /(?<day>[0-9]{2})-(?<month>[a-zA-Z]{3})-(?<year>[0-9]{4})/;
                var timeRegexp = /(?<hour>[0-9]{2}):(?<minute>[0-9]{2}):(?<second>[0-9]{2})/;
                var dropoffdatetime = dropoffInfoElem.datetime;
                var dropoffdate = dropoffdatetime.match(dateRegexp).groups;
                var dropofftime = dropoffdatetime.match(timeRegexp).groups;

                IntMonth = monthStringToInt(dropoffdate.month);

                TimestampElem = toTimestamp(dropoffdate.year, IntMonth, dropoffdate.day, dropofftime.hour, dropofftime.minute, dropofftime.second);
                //console.log(TimestampElem);
                if((currentTimestamp - TimestampElem)<86400){
                    DailyArraydrop.push([new Date(parseInt(dropoffdate.year), parseInt(IntMonth)-1, parseInt(dropoffdate.day), parseInt(dropofftime.hour), parseInt(dropofftime.minute), parseInt(dropofftime.second)),dropoffInfoElem.available_bike_stands])
                }

                if((currentTimestamp - TimestampElem)<604800){
                    WeeklyArraydrop.push([new Date(parseInt(dropoffdate.year), parseInt(IntMonth)-1, parseInt(dropoffdate.day), parseInt(dropofftime.hour), parseInt(dropofftime.minute), parseInt(dropofftime.second)),dropoffInfoElem.available_bike_stands])
                }

            })

            google.charts.load("current", {packages:['corechart', 'bar']});
            google.setOnLoadCallback(function() { drawDailyChartPick(DailyArraypick); });
            google.setOnLoadCallback(function() { drawDailyChartDrop(DailyArraydrop); });

            google.charts.load("current", {packages:['corechart']});
            google.setOnLoadCallback(function() { drawWeeklyChartPick(WeeklyArraypick); });
            google.setOnLoadCallback(function() { drawWeeklyChartDrop(WeeklyArraydrop); });
        }
    });
}

function toTimestamp(year,month,day,hour,minute,second){
    // To get the timestamp in second.
    // One day 86400 seconds.
    // One week 604800 seconds.
    var Timestamp = new Date(Date.UTC(year,month-1,day,hour,minute,second));
    return Timestamp.getTime()/1000;
}

function monthStringToInt(string){
    // Jan, Feb, Mar, Apr, May, Jun, Jul, Aug, Sep, Oct, Nov, Dec.
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


function drawDailyChartPick(DailyArray) {

    var data = new google.visualization.DataTable();
    data.addColumn('datetime', 'Time of Day');
    data.addColumn('number', 'available bikes');

    //console.log(DailyArray);
    data.addRows(DailyArray);

    var options = {
      title: 'Total Available Bikes Throughout the Day',
      height: 450
    };

    var chart = new google.charts.Bar(document.getElementById('chart1_div'));

    chart.draw(data, google.charts.Bar.convertOptions(options));
}



function drawDailyChartDrop(DailyArray) {

    var data = new google.visualization.DataTable();
    data.addColumn('datetime', 'Time of Day');
    data.addColumn('number', 'available bikes');

    //console.log(DailyArray);
    data.addRows(DailyArray);

    var options = {
      title: 'Total Available Bike Stands Throughout the Day',
      height: 450
    };

    var chart = new google.charts.Bar(document.getElementById('chart2_div'));

    chart.draw(data, google.charts.Bar.convertOptions(options));
}

function drawWeeklyChartPick(WeeklyArray) {

    var data = new google.visualization.DataTable();
    data.addColumn('datetime', 'Time of Week');
    data.addColumn('number', 'available bikes');

    //console.log(DailyArray);
    data.addRows(WeeklyArray);

    console.log(data);

    var options = {
      title: 'Total Available Bikes Throughout the Week',
      height: 450
    };

    var chart = new google.visualization.LineChart(document.getElementById('chart3_div'));

    chart.draw(data, options);
}

function drawWeeklyChartDrop(WeeklyArray) {

    var data = new google.visualization.DataTable();
    data.addColumn('datetime', 'Time of Week');
    data.addColumn('number', 'available bike stands');

    //console.log(DailyArray);
    data.addRows(WeeklyArray);

    var options = {
      title: 'Total Available Bike Stands Throughout the Week',
      height: 450
    };

    var chart = new google.visualization.LineChart(document.getElementById('chart4_div'));

    chart.draw(data, options);
}

