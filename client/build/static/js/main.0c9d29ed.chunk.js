(this.webpackJsonpclient=this.webpackJsonpclient||[]).push([[0],{11:function(t,e,n){},13:function(t,e,n){},14:function(t,e,n){"use strict";n.r(e);var r=n(0),c=n(1),a=n.n(c),o=n(5),u=n.n(o),s=(n(11),n(2)),i=n.n(s),l=n(4);function d(){return(d=Object(l.a)(i.a.mark((function t(e,n){return i.a.wrap((function(t){for(;;)switch(t.prev=t.next){case 0:return t.abrupt("return",fetch("http://newsframe:5000/command",{method:"POST",mode:"cors",headers:{"Content-Type":"application/json"},body:JSON.stringify({command:e,arguments:n.join(" ")})}).then(function(){var t=Object(l.a)(i.a.mark((function t(e){var n;return i.a.wrap((function(t){for(;;)switch(t.prev=t.next){case 0:return t.next=2,e.text();case 2:return n=t.sent,t.abrupt("return",n);case 4:case"end":return t.stop()}}),t)})));return function(e){return t.apply(this,arguments)}}()));case 1:case"end":return t.stop()}}),t)})))).apply(this,arguments)}n(13);function m(t){var e=t.children;return Object(r.jsx)("div",{className:"flex flex-grow bg-blue-600 w-screen h-full",children:e})}var f=[{text:"Next",command:"NEXT"},{text:"Update",command:"UPDATE"},{text:"Restart",command:"RESTART"},{text:"Reboot",command:"REBOOT"},{text:"Shutdown",command:"SHUTDOWN"}];var h=function(){var t=function(t,e){(function(t,e){return d.apply(this,arguments)})(t,e).then((function(t){return console.log(t)}))};return Object(r.jsx)(m,{children:Object(r.jsxs)("div",{className:"flex w-full flex-col",children:[Object(r.jsx)("div",{id:"header",className:"w-full bg-blue-500 text-center shadow-md h-16 text-lg",children:Object(r.jsx)("h2",{className:"font-bold mt-4 text-white",children:"NewsFrame Commander"})}),Object(r.jsx)("div",{id:"actions",className:"w-32 ml-auto mr-auto",children:f.map((function(e){return Object(r.jsx)("button",{className:"bg-blue-800 p-3 min-w-full w-full shadow-md rounded-md hover:bg-blue-500",onClick:function(){return t(e.command,[])},children:e.text},e.command)}))})]})})},b=function(t){t&&t instanceof Function&&n.e(3).then(n.bind(null,15)).then((function(e){var n=e.getCLS,r=e.getFID,c=e.getFCP,a=e.getLCP,o=e.getTTFB;n(t),r(t),c(t),a(t),o(t)}))};u.a.render(Object(r.jsx)(a.a.StrictMode,{children:Object(r.jsx)(h,{})}),document.getElementById("root")),b()}},[[14,1,2]]]);
//# sourceMappingURL=main.0c9d29ed.chunk.js.map