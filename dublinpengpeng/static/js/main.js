// the basic functionality JS code
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

            var pickupMarker = document.getElementById("pickUpStation");
            var dropoffMarker = document.getElementById("dropOffStation");
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
                            console.log( weather.temperature);
                            getElementById("temperature").innerHTML = 999 ;

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

function showAllStationMarkers(){
    var url_static = "http://localhost:5000/stations";
    var url_dynamic = "http://localhost:5000/available";

    $.when(
        $.getJSON(url_static),
        $.getJSON(url_dynamic)
    ).done(function(data1, data2){
        var parse1 = data1[0];
        var parse2 = data2[0];
        //console.log(parse1);
        //console.log(parse2);
        if("stations" in parse1 && "available" in parse2){
            var stations = parse1.stations;
            var available = parse2.available;
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
                        map.setCenter(marker.getPosition());

                        var content = "<p>Bike Station: "+station.name+"</p><p>Available bike stands: "+available_bike_stands+"</p><p>Available bikes: "+available_bikes+"</p>";
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
        }
    });
}

function dropdownStationMenu(){
    var selectPickUpStation = "<select id=pickupstation>";
    var selectDropOffStation = "<select id=dropoffstation>";
    selectPickUpStation += "<option value=" + 'selStation' + ">" + 'Select Pick Up Station:' + "</option>"
    selectDropOffStation += "<option value=" + 'selStation' + ">" + 'Select Drop Off Station:' + "</option>"
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

// the front-end UI JS code
!(function($) {
  "use strict";

  // Hero typed
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
          $('.mobile-nav-toggle i').toggleClass('icofont-navigation-menu icofont-close');
        }
        return false;
      }
    }
  });

  $(document).on('click', '.mobile-nav-toggle', function(e) {
    $('body').toggleClass('mobile-nav-active');
    $('.mobile-nav-toggle i').toggleClass('icofont-navigation-menu icofont-close');
  });

  $(document).click(function(e) {
    var container = $(".mobile-nav-toggle");
    if (!container.is(e.target) && container.has(e.target).length === 0) {
      if ($('body').hasClass('mobile-nav-active')) {
        $('body').removeClass('mobile-nav-active');
        $('.mobile-nav-toggle i').toggleClass('icofont-navigation-menu icofont-close');
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

  // jQuery counterUp
  $('[data-toggle="counter-up"]').counterUp({
    delay: 10,
    time: 1000
  });

  // Skills section
  $('.skills-content').waypoint(function() {
    $('.progress .progress-bar').each(function() {
      $(this).css("width", $(this).attr("aria-valuenow") + '%');
    });
  }, {
    offset: '80%'
  });

  // Porfolio isotope and filter
  $(window).on('load', function() {
    var portfolioIsotope = $('.portfolio-container').isotope({
      itemSelector: '.portfolio-item',
      layoutMode: 'fitRows'
    });

    $('#portfolio-flters li').on('click', function() {
      $("#portfolio-flters li").removeClass('filter-active');
      $(this).addClass('filter-active');

      portfolioIsotope.isotope({
        filter: $(this).data('filter')
      });
    });

    // Initiate venobox (lightbox feature used in portofilo)
    $(document).ready(function() {
      $('.venobox').venobox();
    });
  });

  // Testimonials carousel (uses the Owl Carousel library)
  $(".testimonials-carousel").owlCarousel({
    autoplay: true,
    dots: true,
    loop: true,
    responsive: {
      0: {
        items: 1
      },
      768: {
        items: 2
      },
      900: {
        items: 3
      }
    }
  });

  // Portfolio details carousel
  $(".portfolio-details-carousel").owlCarousel({
    autoplay: true,
    dots: true,
    loop: true,
    items: 1
  });

  // Initi AOS
  AOS.init({
    duration: 1000,
    easing: "ease-in-out-back"
  });

})(jQuery);