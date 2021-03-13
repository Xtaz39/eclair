import $ from 'jquery';
import 'ion-rangeslider';
import './sliders';
import './cake-constructor';

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

  $('.add-address').on('click', (e) => {
    e.preventDefault();
    $('.address-field').first().clone().appendTo('.fields');
  });

  $('.modal__close').on('click', function (e) {
    e.preventDefault();
    $(this).parent().parent('.modal').removeClass('active');
  });
  $('.login-btn').on('click', (e) => {
    e.preventDefault();
    const stage1Input = $('.login-stage-1');
    const stage2Input = $('.login-stage-2');
    if (stage2Input.hasClass('active')) {
      // submit form
    } else {
      stage1Input.removeClass('active');
      stage2Input.addClass('active');
      stage1Input.find('input').prop('disabled', true);
      stage1Input.find('button').show();
    }
  });

  $('.input button').on('click', function () {
    $('.login-stage-2').removeClass('active');
    $(this).siblings('input').prop('disabled', false);
    $(this).hide();
  });
});
