(function(){
  var tabs=[].slice.call(document.querySelectorAll('[role=tab]'));
  function select(i,focus){
    tabs.forEach(function(t,j){
      var on=i===j;
      t.setAttribute('aria-selected',on);
      t.tabIndex=on?0:-1;
      document.getElementById(t.getAttribute('aria-controls')).hidden=!on;
    });
    if(focus)tabs[i].focus();
  }
  tabs.forEach(function(t,i){
    t.addEventListener('click',function(){select(i)});
    t.addEventListener('keydown',function(e){
      var n=tabs.length,k=e.key,next=null;
      if(k==='ArrowDown'||k==='ArrowRight')next=(i+1)%n;
      else if(k==='ArrowUp'||k==='ArrowLeft')next=(i-1+n)%n;
      else if(k==='Home')next=0;
      else if(k==='End')next=n-1;
      if(next!==null){e.preventDefault();select(next,true)}
    });
  });
})();

document.querySelectorAll('.photo').forEach(function(box){
  var img=box.querySelector('img');
  function ok(){box.classList.add('ok')}
  function bad(){img.remove()}
  if(img.complete){(img.naturalWidth?ok:bad)()}
  else{img.addEventListener('load',ok);img.addEventListener('error',bad)}
});
