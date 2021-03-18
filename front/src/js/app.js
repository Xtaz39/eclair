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
    const reqInput = $('input[name=request-id]');
    const phoneInput = $('input[name=phone]');

    if (stage2Input.hasClass('active')) {
      $.post("/api/auth/login", {
            "phone": phoneInput.val(),
            "code": $('input[name=code]').val(),
            "request_id": reqInput.val(),
          }
      )
          .done((data) => {
            reqInput.val(data.request_id);
          })
          .fail((data) => {
            console.error(data);
          });
    } else {
      $.post("/api/auth/request-code", {"phone": phoneInput.val()})
          .done((data) => {
            reqInput.val(data.request_id);
          })
          .fail((data) => {
            console.error(data);
          });

      stage1Input.removeClass('active');
      stage2Input.addClass('active');
      stage1Input.find('input').prop('disabled', true);
      stage1Input.find('button').show();
    }
  });

  $('#login-modal button#change-phone').on('click', function (e) {
    e.preventDefault();
    $('.login-stage-2').removeClass('active');
    $(this).siblings('input').prop('disabled', false);
    $(this).hide();
  });

  $('#login-modal button#resend-code').on('click', function (e) {
    e.preventDefault();
    alert("your new code is: 1234")
  });

  $("#sign-in").on("click", (e) => {
    e.preventDefault()
    $('#login-modal').addClass('active')
  })
});
