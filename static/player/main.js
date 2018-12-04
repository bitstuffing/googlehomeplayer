function refresh(){
  //console.log("refreshing...")
  $.getJSON("/track/",function(r){
    total = parseInt(r.duration);
    $("#totalVal").val(total);
    time = parseInt(r.current);
    percent = Math.floor(parseFloat(time / total) * 100)
    //console.log(time)
    minutes = parseInt(time/60);
    seconds = time%60;
    $("#trackTime").text(minutes+":"+seconds);
    percent = percent+"%";
    //console.log(percent)
    $("#progressBar").width(percent);
  });
  setTimeout("refresh()",1000);
}

$(document).ready(function(){

  $("#progressParent").click(function(e){
    console.log(e);
    var x = e.pageX - this.offsetLeft;
    var y = e.pageY - e.offsetY;
    var clickedValue = x*100/$("#progressParent").width();
    console.log(x, $("#progressParent").width(),clickedValue);
    position = parseInt(parseInt($("#totalVal").val())*clickedValue/100);
    $("#status").text(clickedValue+","+position);
    var data = {"seek":position}
    $.post("/seek/",data,function(r){
      console.log(r);
    });
  });

  $("#volumeUp").click(function(){
      $.post("/volume/",{
          "up" : "true",
          "id" : $("#selectedId").val()
      },function(){
          $("#status").text("volume up!");
      });
  });

  $("#volumeDown").click(function(){
      $.post("/volume/",{
          "up" : "false",
          "id" : $("#selectedId").val()
      },function(){
          $("#status").text("volume down!");
      });
  });

  $("#buttonLink").click(function(){
      var link = $("#inputLink").val();
      var encodedLink = encodeURI(btoa(link))
      if($("#videoLink").is(':checked')){
          checked = "true";
      }else{
          checked = "false";
      }
      var data = {
        "url":encodedLink,
        "video":checked,
        "id" : $("#selectedId").val()
      };
      $.post("/play/",data,function(r){console.log(r)});
  });

  $("#stopIcon").click(function(){
      $.post("/stop/",{
          "id" : $("#selectedId").val()
      },function(e){console.log(e)});
  });

  $("#pauseIcon").click(function(){
      $.post("/pause/",{
          "id" : $("#selectedId").val()
      },function(e){console.log(e)});
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
          $("#inputSelectDevice").empty();
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
              $.get("/device/"+value+"/",function(r){
                  console.log(r);
                  $("#selectedId").remove();
                  $("body").append("<input type='hidden' id='selectedId' value='"+r.id+"' />");
                  $("#inputSelectDevice").empty();
              });
              $("#status").text("Selected: "+$("#selectedDevice").val());
          });
      });
  });

  $("#status").text("Ready!");

  refresh()
});
