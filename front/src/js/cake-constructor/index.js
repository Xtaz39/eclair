// CAKE CONSTRUCTOR
import $ from 'jquery';
import 'dropzone/dist/dropzone';

// eslint-disable-next-line no-undef
$(window).on('load', () => {
  (function () {
    const range = $('.js-rangeInput');
    const min = parseFloat($('.js-rangeInput').attr('data-min-weight'));
    const max = parseFloat($('.js-rangeInput').attr('data-max-weight'));
    range.ionRangeSlider({
      min,
      max,
      step: 0.5,
      postfix: ' кг',
      grid: !1,
      onChange(data) {
        $('.cake-weight').text(data.from);
        $('input#weight').val(data.from);
        const peopleCount = (data.from * 6.5).toFixed(0);
        $('.range-wrap__descr .peoples').text(peopleCount);
      },
    });
  }());

  $('a[data-feature-select]').on('click', function (e) {
    e.preventDefault();
    const action = $(this).data('feature-select');

    switch (action) {
      case 'filling':
        $('.feature-modal.feature-filling').addClass('active');
        break;
      case 'design':
        $('.feature-modal.feature-design').addClass('active');
        break;
      case 'decor':
        $('.feature-modal.feature-decor').addClass('active');
        break;
      case 'postcard':
        $('.feature-modal.feature-postcard').addClass('active');
        break;
      default:
        return 0;
    }
    return 0;
  });
  $('.get-back-btn-link').on('click', (e) => {
    e.preventDefault();
    $('.feature-modal').removeClass('active');
  });

  const cakeData = {
    featuresList: {},
    designId: '',
  };

  // Multiple choose of feature
  function initFeatures(features) {
    features.forEach((feature) => {
      cakeData.featuresList[feature] = new Set();
      $(`.feature-filling__item-btn[data-${feature}]`).on('click', function (e) {
        e.preventDefault();
        const parent = $(this).parent('.feature-filling__item');
        const fill = {
          title: parent.find('.feature-filling__item-title').text(),
          src: parent.find('img').attr('src'),
          data: parent.data(feature),
        };
        if (cakeData.featuresList[feature].has(fill.data)) {
          return;
        }

        const image = `
        <div class="cake-filling-item" data-${feature}="${fill.data}">
          <img class="cake-filling-item__image" src="${fill.src}">
          <button class="cake-filling-item__remove" data-${feature}="${fill.data}"></button>
          <span class="cake-filling-item__name">${fill.title}</span>
        </div>
        `;
        $(`.${feature}-images`).append(image);
        parent.addClass('selected');

        cakeData.featuresList[feature].add(fill.data);
        $(`input#${feature}`).val(Array.from(cakeData.featuresList[feature]).join(','));
        $('.feature-modal').removeClass('active');
        // refresh click handler
        $('.cake-filling-item__remove').on('click', function () {
          const fillData = $(this).data(feature);
          cakeData.featuresList[feature].delete(fillData);
          $(`input#${feature}`).val(Array.from(cakeData.featuresList[feature]).join(','));
          $(`.feature-filling__item[data-${feature}=${fillData}]`).removeClass('selected');
          $(`.cake-filling-item[data-${feature}=${fillData}]`).remove();
        });
      });
    });
  }
  initFeatures([
    'feature-fill',
    'feature-decor',
    'feature-postcard',
  ]);
  // Single choose of feature
  // @Todo: refactor it for dynamic feature
  $('.feature-filling__item-btn[data-feature-design]').on('click', function (e) {
    e.preventDefault();
    $('.feature-design .feature-filling__item').removeClass('selected');
    const parent = $(this).parent('.feature-filling__item');
    const fill = {
      src: parent.find('img').attr('src'),
      data: parent.data('feature-design'),
    };

    const image = `<div class="image" style="background-image: url(${fill.src})"></div>`;

    $('.cake-design-images').empty();
    $('.cake-design-images').append(image);
    parent.addClass('selected');

    cakeData.designId = fill.data;
    $('input#design').val(cakeData.designId);
    $('.feature-modal').removeClass('active');
  });
  // CAKE CONSTRUCTOR END
  $('.standard-design-select').on('click', function (e) {
    e.preventDefault();
    const parent = $(this).parent('.feature-filling__item').clone().addClass('selected');
    $('.form-modal').addClass('active');
    $('#selected-design').empty().append(parent);

    $('input#design').val(parent.data('feature-standard-design'));

    $('#selected-design .standard-design-select').on('click', (e) => {
      e.preventDefault();
      $('.form-modal').removeClass('active');
      $('#selected-design').empty();
    });
  });
  $('a[data-tab]').on('click', function (e) {
    e.preventDefault();
    const id = $(this).data('tab');
    $('a[data-tab]').removeClass('active');
    $(this).addClass('active');
    $('div[data-tab]').removeClass('active');
    $(`div[data-tab=${id}]`).addClass('active');
  });
});

Dropzone.options.dropzone = {
  maxFilesize: 2,
  maxFiles: 1,
  acceptedFiles: '.jpeg,.jpg,.png,.gif',
  init() {
    this.on('complete', function (file) {
      if (!file.accepted) {
        return
      }

      $('.feature-design .feature-filling__item').removeClass('selected');

      const img = $('.dz-image > img');
      const image = `<div class="image" style="background-image: url(${img.attr('src')})"></div>`;

      $('.cake-design-images').empty();
      $('.cake-design-images').append(image);
      $('.feature-modal').removeClass('active');

      $('input#design_link').val(file.name);
    });
  }
};
