// function sound(item) {
//     var audio = new Audio('/sounds/VRSpawnSound.mp3');
//     audio.onended = function() { window.location.href="/delete/" + item; }
//     audio.play();
// }

$(document).ready(function() {
  $("#uploadSound").click(function() {
    $("#audioPlayer")[0].play();
  });
});