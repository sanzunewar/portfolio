 (function () {
   document.documentElement.classList.add("js");
   const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

   // Scroll reveal
   const reveals = document.querySelectorAll(".reveal");
   if (reduce || !("IntersectionObserver" in window)) {
     reveals.forEach((el) => el.classList.add("is-visible"));
   } else {
     const io = new IntersectionObserver(
       (entries) => {
         entries.forEach((e) => {
           if (e.isIntersecting) {
             e.target.classList.add("is-visible");
             io.unobserve(e.target);
           }
         });
       },
       { threshold: 0.15 }
     );
     reveals.forEach((el) => io.observe(el));
   }

   // Hero network constellation
   const canvas = document.getElementById("hero-net");
   if (!canvas || reduce) return;
   const ctx = canvas.getContext("2d");
   const dpr = window.devicePixelRatio || 1;
   const COUNT = 46;
   let w, h, nodes;

   function init() {
     const r = canvas.getBoundingClientRect();
     w = canvas.width = r.width * dpr;
     h = canvas.height = r.height * dpr;
     nodes = Array.from({ length: COUNT }, () => ({
       x: Math.random() * w,
       y: Math.random() * h,
       vx: (Math.random() - 0.5) * 0.25 * dpr,
       vy: (Math.random() - 0.5) * 0.25 * dpr,
     }));
   }

   function tick() {
     ctx.clearRect(0, 0, w, h);
     const maxDist = 130 * dpr;
     for (let i = 0; i < nodes.length; i++) {
       const n = nodes[i];
       n.x += n.vx;
       n.y += n.vy;
       if (n.x < 0 || n.x > w) n.vx *= -1;
       if (n.y < 0 || n.y > h) n.vy *= -1;
       for (let j = i + 1; j < nodes.length; j++) {
         const m = nodes[j];
         const dist = Math.hypot(n.x - m.x, n.y - m.y);
         if (dist < maxDist) {
           ctx.strokeStyle = `rgba(91,141,239,${(1 - dist / maxDist) * 0.35})`;
           ctx.lineWidth = dpr;
           ctx.beginPath();
           ctx.moveTo(n.x, n.y);
           ctx.lineTo(m.x, m.y);
           ctx.stroke();
         }
       }
       ctx.fillStyle = "rgba(63,199,212,0.85)";
       ctx.beginPath();
       ctx.arc(n.x, n.y, 1.6 * dpr, 0, Math.PI * 2);
       ctx.fill();
     }
     requestAnimationFrame(tick);
   }

   init();
   tick();
   let t;
   window.addEventListener("resize", () => {
     clearTimeout(t);
     t = setTimeout(init, 200);
   });
 })();
