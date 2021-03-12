import $ from 'jquery';
import 'slick-carousel';
import 'ion-rangeslider';

if (module.hot) {
  module.hot.accept();
}


// eslint-disable-next-line no-undef
$(window).on('load', () => {
  function scrollHandler() {
    // eslint-disable-next-line no-undef
    if ($(window).scrollTop() > 400) {
      $('.header__bottom.fixed').addClass('active');
    } else {
      $('.header__bottom.fixed').removeClass('active');
    }
  }
  scrollHandler();
  // eslint-disable-next-line no-undef
  $(window).on('scroll', () => {
    scrollHandler();
  });


  // eslint-disable-next-line no-undef
  if (!window.localStorage.getItem('cookies_accepted')) {
    $('.cookies').show();
  }

  $('.cookies__close').on('click', (e) => {
    e.preventDefault();
    $('.cookies').hide();
    // eslint-disable-next-line no-undef
    window.localStorage.setItem('cookies_accepted', 'true');
  });

  $('.burger').on('click', (e) => {
    e.preventDefault();
    $('.header__wrap').toggleClass('active');
  });

  $('.hero__slider').slick({
    dots: false,
    infinite: true,
    slidesToShow: 1,
    slidesToScroll: 1,
    autoplay: true,
    autoplaySpeed: 5000,
    pauseOnFocus: true,
    pauseOnHover: true,
    prevArrow: $('.slider__buttons--prev'),
    nextArrow: $('.slider__buttons--next'),
  });

  $('.carousel').slick({
    infinite: true,
    prevArrow: $('.buttons .prev'),
    nextArrow: $('.buttons .next'),
  });

  $('.carousel-recommended').slick({
    infinite: true,
    slidesToShow: 2,
    arrows: false,
    responsive: [
      {
        breakpoint: 500,
        settings: {
          slidesToShow: 1,
        },
      },
    ],
  });

  $('.items-switch__top').slick({
    infinite: true,
    arrows: false,
    slidesToShow: 1,
    asNavFor: $('.items-switch__bottom'),
  });

  $('.items-switch__bottom').slick({
    infinite: true,
    arrows: false,
    slidesToShow: 6,
    focusOnSelect: true,
    asNavFor: $('.items-switch__top'),
  });

  $('.item__actions').on('click', function actionItemsClickHandler(e) {
    const num = +$(this).find('.item__quantity-text').text();

    if ($(e.target).hasClass('item__btn--minus') && num > 1) {
      $(this).find('.item__quantity-text').text(num - 1);
    }

    if ($(e.target).hasClass('item__btn--plus')) {
      $(this).find('.item__quantity-text').text(num + 1);
    }

    if ($(e.target).hasClass('btn')) {
      e.preventDefault();
      $(this).find('.item__quantity-text').text(1);
    }
  });

  $('.add-address').on('click', function addAddressHandler(e) {
    e.preventDefault();
    $('.address-field').first().clone().appendTo('.fields');
  });


  // CAKE CONSTRUCTOR
  (function() {
    var e = $(".js-rangeInput")
      , t = parseFloat($(".js-rangeInput").attr("data-min-weight"))
      , n = parseFloat($(".js-rangeInput").attr("data-max-weight"));
    e.ionRangeSlider({
      min: t,
      max: n,
      step: .5,
      postfix: " кг",
      grid: !1,
      onChange (data) {
        $('.cake-weight').text(data.from)
        $('input#weight').val(data.from)
        const peopleCount = (data.from * 6.5).toFixed(0)
        $('.range-wrap__descr .peoples').text(peopleCount)
      }
    })
  })();

  $('a[data-feature-select]').on('click', function (e) {
    e.preventDefault()
    const action = $(this).data('feature-select');

    switch (action) {
      case 'filling':
        $('.feature-modal.feature-filling').addClass('active')
        break
      case 'design':
        $('.feature-modal.feature-design').addClass('active')
        break
    }
  })
  $('.get-back-btn-link').on('click', function (e) {
    e.preventDefault()
    $('.feature-modal').removeClass('active')
  })

  const filledIds = new Set()
  const cakeData = {
    fillIds: [],
    designId: ''
  }

  $('.feature-filling__item-btn[data-feature-fill]').on('click', function (e) {
    e.preventDefault()
    const parent = $(this).parent('.feature-filling__item')
    const fill = {
      title: parent.find('.feature-filling__item-title').text(),
      src: parent.find('img').attr('src'),
      data: parent.data('feature-fill')
    }
    if (filledIds.has(fill.data)) { return }

    const image = `
    <div class="cake-filling-item" data-feature-fill="${fill.data}">
      <img class="cake-filling-item__image" src="${fill.src}">
      <button class="cake-filling-item__remove" data-feature-fill="${fill.data}"></button>
      <span class="cake-filling-item__name">${fill.title}</span>
    </div>
    `
    $('.cake-order-images').append(image)
    parent.addClass('selected')

    filledIds.add(fill.data)
    cakeData.fillIds.push(fill.data)
    $('input#fills').val(cakeData.fillIds.join(','))

    // refresh click handler
    $('.cake-filling-item__remove').on('click', function () {
      const fillData = $(this).data('feature-fill')
      filledIds.delete(fillData)
      cakeData.fillIds = cakeData.fillIds.filter(id => id !== fillData)
      $('input#fills').val(cakeData.fillIds.join(','))
      $(`.feature-filling__item[data-feature-fill=${fillData}]`).removeClass('selected')
      $(`.cake-filling-item[data-feature-fill=${fillData}]`).remove()
    })
  })

  $('.feature-filling__item-btn[data-feature-design]').on('click', function (e) {
    e.preventDefault()
    $('.feature-design .feature-filling__item').removeClass('selected')
    const parent = $(this).parent('.feature-filling__item')
    const fill = {
      src: parent.find('img').attr('src'),
      data: parent.data('feature-design')
    }
    parent.find('input:radio').prop("checked", true).trigger("click")

    const image = `<div class="image" style="background-image: url(${fill.src})"></div>`

    $('.cake-design-images').empty()
    $('.cake-design-images').append(image)
    parent.addClass('selected')

    cakeData.designId = fill.data
    $('input#design').val(cakeData.designId)
  })
  // CAKE CONSTRUCTOR END

  $('.modal__close').on('click', function (e) {
    e.preventDefault()
    $(this).parent().parent('.modal').removeClass('active')
  })
  $('.login-btn').on('click', function (e) {
    e.preventDefault()
    const stage1Input = $('.login-stage-1')
    const stage2Input = $('.login-stage-2')
    if(stage2Input.hasClass('active')) {
      // submit form
    } else {
      stage1Input.removeClass('active')
      stage2Input.addClass('active')
      stage1Input.find('input').prop('disabled', true)
      stage1Input.find('button').show()
    }
  })

  $('.input button').on('click', function () {
    $('.login-stage-2').removeClass('active')
    $(this).siblings('input').prop('disabled', false)
    $(this).hide()
  })

});
