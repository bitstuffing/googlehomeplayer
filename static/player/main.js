
$(document).ready(function(){

  $("#buttonLink").click(function(){
    var link = $("#inputLink").val();
    var encodedLink = encodeURI(btoa(link))
    $.post("/play/",{"url":encodedLink},function(r){console.log(r)});
  });

  $("#stopIcon").click(function(){
    $.get("/stop/",function(e){console.log(e)});
  });

  $("#pauseIcon").click(function(){
    $.get("/pause/",function(e){console.log(e)});
  });

  $("#selectDevice").click(function(){
    $("#status").text("Obtaining devices...");
    $("#loadingSpin").show();
    $("#inputSelectDevice").hide();
    $("#inputSelectDevice").attr("disabled","");
    $.getJSON("/devices/",function(response){
      $("#status").text("Select one device");
      $("#inputSelectDevice").removeAttr("disabled");
      $("#loadingSpin").hide();
      $("#inputSelectDevice").show();
      $.each(response,function(i,value){
        var option = "<option value='"+value+"'>"+value+"</option>";
        $("#inputSelectDevice").append(option);
      });
      $("#inputSelectDevice").change(function(){
          var value = $(this).val();
          $("#selectedDevice").val(value);
          //$('#modalDevice').modal().hide();
          $("#modalDevice .close").click();
          $.get("/device/"+value+"/",function(r){console.log(r)});
          $("#status").text("Selected: "+$("#selectedDevice").val());
      });
    });
  });

  $("#status").text("Ready!");

});
