
$(document).ready(function(){

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

});
