(function($){
  "use strict";

  var $window = $(window);

  $window.on('load', function() {
    $window.trigger("resize");
  });

  // Preloader
  $('.loader').fadeOut();
  $('.loader-mask').delay(350).fadeOut('slow');


  // Init
  initOwlCarousel();


  $window.on('resize', function() {
    hideSidenav();
    initIsotope();
  });


  /* Detect Browser Size
  -------------------------------------------------------*/
  var minWidth;
  if (Modernizr.mq('(min-width: 0px)')) {
    // Browsers that support media queries
    minWidth = function (width) {
      return Modernizr.mq('(min-width: ' + width + 'px)');
    };
  }
  else {
    // Fallback for browsers that does not support media queries
    minWidth = function (width) {
      return $window.width() >= width;
    };
  }


  /* Mobile Detect
  -------------------------------------------------------*/
  if (/Android|iPhone|iPad|iPod|BlackBerry|Windows Phone/i.test(navigator.userAgent || navigator.vendor || window.opera)) {
     $("html").addClass("mobile");
     $('.dropdown-toggle').attr('data-toggle', 'dropdown');
  }
  else {
    $("html").removeClass("mobile");
  }

  /* IE Detect
  -------------------------------------------------------*/
  if(Function('/*@cc_on return document.documentMode===10@*/')()){ $("html").addClass("ie"); }


  /* Sticky Navigation
  -------------------------------------------------------*/
  $window.scroll(function(){
    scrollToTop();
    stickyNav();
  });

  var $stickyNav = $('.nav--sticky');
  var $nav = $('.nav');

  function stickyNav() {
    if ($window.scrollTop() > 2) {
      $stickyNav.addClass('sticky');
      $nav.addClass('sticky');
    } else {
      $stickyNav.removeClass('sticky');
      $nav.removeClass('sticky');
    }
  }


  /* Mobile Navigation
  -------------------------------------------------------*/
  var $sidenav = $('#sidenav'),
      $mainContainer = $('#main-container'),
      $navIconToggle = $('.nav-icon-toggle'),
      $navHolder = $('.nav__holder'),
      $contentOverlay = $('.content-overlay'),
      $htmlContainer = $('html'),
      $sidenavCloseButton = $('#sidenav__close-button');


  $navIconToggle.on('click', function(e) {
    e.stopPropagation();
    $(this).toggleClass('nav-icon-toggle--is-open');
    $sidenav.toggleClass('sidenav--is-open');
    $contentOverlay.toggleClass('content-overlay--is-visible');
    // $htmlContainer.toggleClass('oh');
  });

  function resetNav() {
    $navIconToggle.removeClass('nav-icon-toggle--is-open');
    $sidenav.removeClass('sidenav--is-open');
    $contentOverlay.removeClass('content-overlay--is-visible');
    // $htmlContainer.removeClass('oh');
  }

  function hideSidenav() {
    if( minWidth(992) ) {
      resetNav();
    }
  }

  $contentOverlay.on('click', function() {
    resetNav();
  });

  $sidenavCloseButton.on('click', function() {
    resetNav();
  });


  var $dropdownTrigger = $('.nav__dropdown-trigger'),
      $navDropdownMenu = $('.nav__dropdown-menu'),
      $navDropdown = $('.nav__dropdown');


  if ( $('html').hasClass('mobile') ) {

    $('body').on('click',function() {
      $navDropdownMenu.addClass('hide-dropdown');
    });

    $navDropdown.on('click', '> a', function(e) {
      e.preventDefault();
    });

    $navDropdown.on('click',function(e) {
      e.stopPropagation();
      $navDropdownMenu.removeClass('hide-dropdown');
    });
  }


  /* Sidenav Menu
  -------------------------------------------------------*/
  $('.sidenav__menu-toggle').on('click', function(e) {
    e.preventDefault();

    var $this = $(this);

    $this.parent().siblings().removeClass('sidenav__menu--is-open');
    $this.parent().siblings().find('li').removeClass('sidenav__menu--is-open');
    $this.parent().find('li').removeClass('sidenav__menu--is-open');
    $this.parent().toggleClass('sidenav__menu--is-open');

    if ($this.next().hasClass('show')) {
      $this.next().removeClass('show').slideUp(350);
    } else {
      $this.parent().parent().find('li .sidenav__menu-dropdown').removeClass('show').slideUp(350);
      $this.next().toggleClass('show').slideToggle(350);
    }
  });


  /* Nav Search
  -------------------------------------------------------*/
  (function() {
    var $navSearchForm = $('.nav__search-form'),
        $navSearchTrigger = $('.nav__search-trigger'),
        $navSearchInput = $('.nav__search-input'),
        $navSearchClose = $('.nav__search-close');

    $navSearchTrigger.on('click',function(e){
      e.preventDefault();
      $navSearchForm.animate({opacity: 'toggle'},500);
      $navSearchInput.focus();
    });

    $navSearchClose.on('click',function(e){
      e.preventDefault();
      $navSearchForm.animate({opacity: 'toggle'},500);
    });

    function closeSearch(){
      $navSearchForm.fadeOut(200);
    }

    $(document.body).on('click',function(e) {
      closeSearch();
    });

    $navSearchInput.add($navSearchTrigger).on('click',function(e) {
      e.stopPropagation();
    });
  })();


  /* Crypto Rates
  -------------------------------------------------------*/
  var $cryptoRates = $('.crypto-rates');
  $cryptoRates.append('<span class="loading">Loading...</span>');

  $.ajax({
    type: 'GET',
    url: 'https://api.coinmarketcap.com/v1/ticker/?limit=10',
    dataType: 'json',
    success: function(response) {
      renderData(response);
    },
    error: function(jqXHR, textStatus) {
      console.log(textStatus);
    }
  });

  function renderData(data) {
    var html = '';
    var percentChange = '';
    var minusRE = '';

    for (var i = 0; i < data.length; i++) {
      html += "<div>" + "<img class='crypto-rates__img' src='static/img/coins_icons/" + data[i].id + "_icon.png'/>" + "<span class='crypto-rates__name'>" + data[i].name + " (" + data[i].symbol + ")" + "</span>" + "<span class='crypto-rates__price'>$" + data[i].price_usd + "</span>";

      percentChange = data[i].percent_change_1h;
      minusRE = percentChange.search(/\-/);

      html += "<span class='crypto-rates__percent " + priceChange() + "'>" + data[i].percent_change_1h + "%</span>" + "</div>";
    }

    //  Find minus
    function priceChange() {
      if (minusRE === 0) {
        return 'crypto-rates__percent--down';
      } else {
        return 'crypto-rates__percent--up';
      }
    }
    priceChange();

    $cryptoRates.append(html);
    $('.loading').remove();


    // Ticker
    $('.marquee').marquee({
      pauseOnHover: true,
      // delayBeforeStart: -20000,
      gap: 0,
      duplicated: true,
      startVisible: true
    });
  }


  /* Sticky sidebar
  -------------------------------------------------------*/
  (function() {
    var $stickyCol = $('.sticky-col');
    if($stickyCol.length > 0) {
      $stickyCol.stick_in_parent({
        offset_top: 40
      });
    }
  })();


  /* Isotope
  -------------------------------------------------------*/
  function initIsotope() {
    var $isotopeGrid = $('#isotope-grid');
    if($isotopeGrid.length > 0) {
      $isotopeGrid.imagesLoaded( function() {
        $isotopeGrid.isotope({
          layoutMode: 'masonry'
        });
        $isotopeGrid.isotope();
      });
    }
  }


  /* Tabs
  -------------------------------------------------------*/
  $('.tabs__trigger').on('click', function(e) {
    var currentAttrValue = $(this).attr('href');
    $('.tabs__content-trigger ' + currentAttrValue).stop().fadeIn(1000).siblings().hide();
    $(this).parent('li').addClass('tabs__item--active').siblings().removeClass('tabs__item--active');
    e.preventDefault();
  });


  /* Owl Carousel
  -------------------------------------------------------*/
  function initOwlCarousel(){

    // Hero
    $("#owl-hero-grid").owlCarousel({
      center: false,
      items: 1,
      loop: true,
      nav: true,
      dots: true,
      margin: 0,
      lazyLoad: true,
      navSpeed: 500,
      navText: ['<i class="ui-arrow-left">','<i class="ui-arrow-right">']
    });

    // Single Image
    $("#owl-single").owlCarousel({
      items: 1,
      loop: true,
      nav: true,
      dots: false,
      lazyLoad: true,
      navSpeed: 500,
      navText: ['<i class="ui-arrow-left">','<i class="ui-arrow-right">']
    });

    // Single Post Gallery
    $("#owl-single-post-gallery").owlCarousel({
      items: 1,
      loop: true,
      nav: true,
      dots: true,
      lazyLoad: true,
      navSpeed: 500,
      navText: ['<i class="ui-arrow-left">','<i class="ui-arrow-right">']
    });

    // Custom nav
    var owlNav = $('#owl-posts').owlCarousel();
    $(".carousel-nav__btn--prev").on('click', function () {
        owlNav.trigger('prev.owl.carousel');
    });

    $(".carousel-nav__btn--next").on('click', function () {
        owlNav.trigger('next.owl.carousel');
    });
  };


  /* ---------------------------------------------------------------------- */
  /*  Contact Form
  /* ---------------------------------------------------------------------- */

  var submitContact = $('#submit-message'),
    message = $('#msg');

  submitContact.on('click', function(e){
    e.preventDefault();

    var $this = $(this);

    $.ajax({
      type: "POST",
      url: 'contact.php',
      dataType: 'json',
      cache: false,
      data: $('#contact-form').serialize(),
      success: function(data) {

        if(data.info !== 'error'){
          $this.parents('form').find('input[type=text],input[type=email],textarea,select').filter(':visible').val('');
          message.hide().removeClass('success').removeClass('error').addClass('success').html(data.msg).fadeIn('slow').delay(5000).fadeOut('slow');
        } else {
          message.hide().removeClass('success').removeClass('error').addClass('error').html(data.msg).fadeIn('slow').delay(5000).fadeOut('slow');
        }
      }
    });
  });


  /* Scroll to Top
  -------------------------------------------------------*/
  function scrollToTop() {
    var scroll = $window.scrollTop();
    var $backToTop = $("#back-to-top");
    if (scroll >= 50) {
      $backToTop.addClass("show");
    } else {
      $backToTop.removeClass("show");
    }
  }

  $('a[href="#top"]').on('click',function(){
    $('html, body').animate({scrollTop: 0}, 1000, "easeInOutQuint");
    return false;
  });

})(jQuery);
