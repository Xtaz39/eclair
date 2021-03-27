import $ from 'jquery';
import 'ion-rangeslider';
import './sliders';
import './cake-constructor';
import 'bootstrap/js/dist/dropdown';

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


  $('.add-address').on('click', (e) => {
    e.preventDefault();
    const addresField = $('.address-field').first().clone();
    addresField.find("input").val("");
    addresField.appendTo('.fields');

    if ($("input[name=addresses]").length >= 5) {
        $(e.target).remove();
    }
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
      const resendBtn = $('#resend-code');
      const errsList = $('#login-modal .errorlist')

      errsList.empty();

      if (stage2Input.hasClass('active')) {
          $.post("/api/confirm-action", {
                  "phone": phoneInput.val(),
                  "code": $('input[name=code]').val(),
                  "request_id": reqInput.val(),
              }
          )
              .done(() => {
                  location.reload();
          })
          .fail((xhr, textStatus, error) => {
            const errors = xhr.responseJSON.errors
              Object.keys(errors).forEach((key) => {
                  errors[key].forEach((v) => {
                      $("#err-" + key).append("<li>" + v + "</li>");
                  })
              });
          });
    } else {
          $.post("/api/request-code", {
              "phone": phoneInput.val(),
              "action": $('input[name=action]').val(),
          })
          .done((data) => {
              reqInput.val(data.request_id);

              stage1Input.removeClass('active');
              stage2Input.addClass('active');
              stage1Input.find('input').prop('disabled', true);
              stage1Input.find('button').show();

              resendBtn.prop('disabled', true);
              setInterval(() => {
                  resendBtn.prop('disabled', false);
              }, 60000)

          })
          .fail((xhr, textStatus, error) => {
              const errors = xhr.responseJSON.errors
              Object.keys(errors).forEach((key) => {
                  errors[key].forEach((v) => {
                      $("#err-" + key).append("<li>" + v + "</li>");
                  })
              });
          });
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
      const resendBtn = $('#resend-code');
      resendBtn.prop('disabled', true);
      const errsList = $('#login-modal .errorlist')
      errsList.empty();

      $.post("/api/request-code", {"phone": $('input[name=phone]').val()})
          .done((data) => {
              $('input[name=request-id]').val(data.request_id);
              setInterval(() => {
                  resendBtn.prop('disabled', false);
              }, 60000)
          })
          .fail((xhr, textStatus, error) => {
              resendBtn.prop('disabled', false);
              const errors = xhr.responseJSON.errors
              Object.keys(errors).forEach((key) => {
                  errors[key].forEach((v) => {
                      $("#err-" + key).append("<li>" + v + "</li>");
                  })
              });
          });
  });

  $("#sign-in").on("click", (e) => {
    e.preventDefault()
    $('#login-modal').addClass('active')
  })

  $(".order-form .dropdown-menu a").on("click", (e) => {
      e.preventDefault();
      const value = e.target.innerHTML;
      const fieldName = e.target.attributes['data-input-field'].value;
      $('input[name=' + fieldName + ']').val(value);
  })
});
