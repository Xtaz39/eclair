/* eslint-disable */
import $ from 'jquery';
import 'jquery-ui/ui/widgets/datepicker';
import 'ion-rangeslider';
import './sliders';
import './cake-constructor';
import 'bootstrap/js/dist/dropdown';

$(window).on('load', () => {
  $('body').addClass('loaded');
});


// eslint-disable-next-line no-undef
$(window).on('load', () => {
  /* Локализация datepicker */
  $.datepicker.regional['ru'] = {
    closeText: 'Закрыть',
    prevText: 'Предыдущий',
    nextText: 'Следующий',
    currentText: 'Сегодня',
    monthNames: ['Январь','Февраль','Март','Апрель','Май','Июнь','Июль','Август','Сентябрь','Октябрь','Ноябрь','Декабрь'],
    monthNamesShort: ['Янв','Фев','Мар','Апр','Май','Июн','Июл','Авг','Сен','Окт','Ноя','Дек'],
    dayNames: ['воскресенье','понедельник','вторник','среда','четверг','пятница','суббота'],
    dayNamesShort: ['вск','пнд','втр','срд','чтв','птн','сбт'],
    dayNamesMin: ['Вс','Пн','Вт','Ср','Чт','Пт','Сб'],
    weekHeader: 'Не',
    dateFormat: 'dd.mm.yy',
    firstDay: 1,
    isRTL: false,
    showMonthAfterYear: false,
    yearSuffix: ''
  };
  $.datepicker.setDefaults($.datepicker.regional['ru']);
  $('input.datepicker-input').datepicker();
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

  if (window.location.hash) {
    setTimeout(() => {
      $('html, body').animate({
        scrollTop: $(decodeURIComponent(window.location.hash)).offset().top
      }, 800);
    }, 500)
  }
  $("a").on('click', function(event) {
    if (this.hash !== "") {
      console.log(this.hash);
      event.preventDefault();
      let hash = decodeURIComponent(this.hash);
      if (document.querySelector(hash)) {
        $('html, body').animate({
          scrollTop: $(hash).offset().top
        }, 800, function(){
          window.location.hash = hash;
        });
      } else {
        window.location.href = window.location.origin + hash
      }
    }
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
    const errsList = $('#login-modal .errorlist');

    errsList.empty();

    if (stage2Input.hasClass('active')) {
      $.post('/api/confirm-action', {
        phone: phoneInput.val(),
        code: $('input[name=code]').val(),
        request_id: reqInput.val(),
      })
        .done(() => {
          location.reload();
        })
        .fail((xhr, textStatus, error) => {
          const { errors } = xhr.responseJSON;
          Object.keys(errors).forEach((key) => {
            errors[key].forEach((v) => {
              $(`#err-${key}`).append(`<li>${v}</li>`);
            });
          });
        });
    } else {
      $.post('/api/request-code', {
        phone: phoneInput.val(),
        action: $('input[name=action]').val(),
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
          }, 60000);
        })
        .fail((xhr, textStatus, error) => {
          const { errors } = xhr.responseJSON;
          Object.keys(errors).forEach((key) => {
            errors[key].forEach((v) => {
              $(`#err-${key}`).append(`<li>${v}</li>`);
            });
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

  $('#login-modal button#resend-code').on('click', (e) => {
    e.preventDefault();
    const resendBtn = $('#resend-code');
    resendBtn.prop('disabled', true);
    const errsList = $('#login-modal .errorlist');
    errsList.empty();

    $.post('/api/request-code', { phone: $('input[name=phone]').val() })
      .done((data) => {
        $('input[name=request-id]').val(data.request_id);
        setInterval(() => {
          resendBtn.prop('disabled', false);
        }, 60000);
      })
      .fail((xhr, textStatus, error) => {
        resendBtn.prop('disabled', false);
        const { errors } = xhr.responseJSON;
        Object.keys(errors).forEach((key) => {
          errors[key].forEach((v) => {
            $(`#err-${key}`).append(`<li>${v}</li>`);
          });
        });
      });
  });

  $('#sign-in').on('click', (e) => {
    e.preventDefault();
    $('#login-modal').addClass('active');
  });

  $('#sign-in-cart').on('click', (e) => {
    e.preventDefault();
    $('#login-modal').addClass('active');
  });


  $('.order-form .dropdown-menu a').on('click', (e) => {
    e.preventDefault();
    const street = e.target.attributes['data-street'].value;
    const house = e.target.attributes['data-house'].value;
    const room = e.target.attributes['data-room'].value;
    const entrance = e.target.attributes['data-entrance'].value;
    const floor = e.target.attributes['data-floor'].value;
    const doorphone = e.target.attributes['data-doorphone'].value;

    $('input[name=street]').val(street);
    $('input[name=house]').val(house);
    $('input[name=room]').val(room);
    $('input[name=entrance]').val(entrance);
    $('input[name=floor]').val(floor);
    $('input[name=doorphone]').val(doorphone);
  });

  $('label.address-field a.delete-address').on('click', (e) => {
    e.preventDefault();

    const target = $(e.currentTarget);
    $.post('/api/delete-user-address', { address_id: target.data('addr-id') })
      .done((data) => {
        target.closest('.address-field').hide();
      })
      .fail((xhr, textStatus, error) => {
        console.log(xhr.responseJSON);
      });
  });
});

ymaps.ready(init);

function init() {
    var suggestView1 = new ymaps.SuggestView('street');
}