import $ from 'jquery';
import 'slick-carousel';

$(window).on('load', () => {
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
});