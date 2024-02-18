// For cursor
function cursor() {
  let cursor = document.querySelector("#cursor");
  let body = document.querySelector("body")

  body.addEventListener("mousemove", (e)=>{
    gsap.to(cursor, {
      x: e.x + "px",
      y: e.y + "px",
    })
  })
}
cursor()
//  For page1 movement
function section1() {
  let t1 = gsap.timeline();
  t1.from("nav", {
    y: -50,
    opacity: 0,
    duration: 1,
  })
  t1.from("#page-bottom h1, #page-bottom p", {
    y:100,
    opacity: 0,
    duration: 0.8
  })
}
section1()


gsap.to("#page>video", {
  ScrollTrigger:{
    trigger: `#page>video`,
    start: `3% top`,
    end: `bottom top`,
    markers: true,
    scroller: `#main`
  },
  onStart:()=>{
    document.querySelector("#page>video").play()
  }
})


window.onscroll = ()=> {
  menu.classList.remove('fa-times');
  menu.classList.remove('active');
}
var swiper = new Swiper(".home-slider", {
  loop: true,
  spaceBetween: true,
  grabCursor: true,
  pagination: {
    el: ".swiper-pagination",
    clickable: true,
  },
});


// For website smooth scrolling
function loco() {
    gsap.registerPlugin(ScrollTrigger);

const locoScroll = new LocomotiveScroll({
  el: document.querySelector(".#main"),
  smooth: true,

  // for tablet smooth
  tablet: { smooth: true },

  // for mobile
  smartphone: { smooth: true }
});
locoScroll.on("scroll", ScrollTrigger.update);

ScrollTrigger.scrollerProxy(".#main", {
  scrollTop(value) {
    return arguments.length ? locoScroll.scrollTo(value, 0, 0) : locoScroll.scroll.instance.scroll.y;
  },
  getBoundingClientRect() {
    return {
      top: 0, left: 0, width: window.innerWidth, height: window.innerHeight
    };
  },

  // follwoing line is not required to work pinning on touch screen
   pinType: document.querySelector(".#main").style.transform
    ? "transform": "fixed"
});

ScrollTrigger.addEventListener("refresh", () => locoScroll.update());

ScrollTrigger.refresh();

}

loco()

gsap.to("#page>video", {
    ScrollTrigger: {
        trigger: `#page>video`,
        start: `7% top`,
        end: `bottom top`,
        markers: true,
        scroller: `#main`
    },
    onStart:()=>{
        document.querySelector("#page>video").play()
    }
})