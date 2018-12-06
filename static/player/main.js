function refresh(){
  //console.log("refreshing...")

  $.getJSON("/playlist/",function(response){
    $("#currentPlaylist").children().remove();
    $.each(response.tracks,function(i,r){
      var hidden = " <input type='hidden' name='track_url' value='"+r.url+"' > ";
      var element = '<li class="list-group-item">'+r.name+hidden+'</li>';
      $("#currentPlaylist").append(element);
    });
  });

  $.getJSON("/track/",function(r){
    total = parseInt(r.duration);
    $("#totalVal").val(total);
    time = parseInt(r.current);
    percent = 0;
    if(total > 0){
      percent = Math.floor(parseFloat(time / total) * 100)
    }
    //console.log(time)
    minutes = parseInt(time/60);
    if(minutes > 60){
      //TODO with config
    }
    seconds = time%60;
    if(seconds < 10){
      seconds = "0"+seconds;
    }
    $("#trackTime").text(minutes+":"+seconds);
    percent = percent+"%";
    //console.log(percent)
    $("#progressBar").width(percent);
  });
  setTimeout("refresh()",1000);
}

function deletePlaylist(id){
  $.post("/playlist/",{"id":id,"action":"delete"},function(response){
    $("#playlistLink").trigger("click");
  });
}

function editPlaylist(id){

}

function selectPlaylist(id){
  $.post("/playlist/",{"id":id,"action":"select"},function(response){
    $("#currentPlaylistLink").trigger("click");
  });
}

$(document).ready(function(){

  $(".nav-link").on("touched click",function(e){
    $(".active").removeClass("active")
    $(this).parent().addClass("active");
    $("#status").text("Current is: "+$(this).text());
    var selected = $(this).attr("id");
    if(selected == 'currentPlaylistLink'){
      $("#rowPlaylist").addClass("d-none");
      $("#rowCurrentPlaylist").removeClass("d-none");
    }else if (selected == 'playlistLink'){
      $("#rowPlaylist").removeClass("d-none");
      $("#rowCurrentPlaylist").addClass("d-none");
      $("#playlistList").children().remove();
      $.post("/playlist/",{"id":"all"},function(response){
        var res = $.parseJSON(response);
        $.each(res.playlists,function(i,r){
          console.log(r);
          var edit = '<i onclick="editPlaylist(\''+r.id+'\')"  class="far fa-edit" style="float:right;cursor:pointer;margin-right: 5px;"></i> ';
          var trash = ' <i onclick="deletePlaylist(\''+r.id+'\')" class="fa fa-trash" aria-hidden="true" style="float:right;cursor:pointer;"></i>';
          var target = '<span onclick="selectPlaylist(\''+r.id+'\')" style="cursor:pointer;">'+r.name+'</span>';
          var element = '<li class="list-group-item">'+target+trash+edit+'</li>';
          $("#playlistList").append(element);
        });
      });
    }
  });

  $("#progressParent").on('touchend click',function(e){
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

  $("#volumeUp").on('touchend click',function(){
      $.post("/volume/",{
          "up" : "true",
          "id" : $("#selectedId").val()
      },function(){
          $("#status").text("volume up!");
      });
  });

  $("#volumeDown").on('touchend click',function(){
      $.post("/volume/",{
          "up" : "false",
          "id" : $("#selectedId").val()
      },function(){
          $("#status").text("volume down!");
      });
  });

  $("#buttonLink").on('touchend click',function(){
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

  $("#stopIcon").on('touchend click',function(){
      $.post("/stop/",{
          "id" : $("#selectedId").val()
      },function(e){console.log(e)});
  });

  $("#pauseIcon").on('touchend click',function(){
      $.post("/pause/",{
          "id" : $("#selectedId").val()
      },function(e){console.log(e)});
  });

  $("#selectDevice").on('touchend click',function(){
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

  refresh();
});
