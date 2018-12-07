function refresh(){
  //console.log("refreshing...")

  $.getJSON("/playlist/",function(response){
    $("#currentPlaylist").children().remove();
    if($("#hiddenSelectedTrack").length > 0){
      var hiddenValue = $("#hiddenSelectedTrack").val()
    }
    $.each(response.tracks,function(i,r){
      var hidden = " <input type='hidden' name='track_url' value='"+r.url+"' > ";
      var classes = "list-group-item ";
      if (hiddenValue == r.id){
        classes += 'active';
      }
      var span = '<span onclick="selectTrack(\''+r.id+'\')" ontouchend="selectTrack(\''+r.id+'\')" style="cursor:pointer;">'+r.name+'</span>';
      var element = '<li id="playlist_track_'+r.id+'" class="'+classes+'">'+span+hidden+'</li>';
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
    if(r.track_name != undefined){
      var trackName = "";
      if(r.track_text != undefined){
        trackName = r.track_text+" - ";
      }
      trackName += r.track_name;
      $("#trackName").text(trackName);
      //$("[id^='playlist_track_']").not("#playlist_track_"+r.track_id).removeClass("active");
      //$("#playlist_track_"+r.track_id).addClass("active");
      if(r.track_id != undefined){
        $("#hiddenSelectedTrack").remove();
        $("body").append("<input type='hidden' id='hiddenSelectedTrack' value='"+r.track_id+"' >");
      }
    }else{
      $("#trackName").text(" ");
    }
    $("#trackTime").text(minutes+":"+seconds);
    percent = percent+"%";
    //console.log(percent)
    $("#progressBar").width(percent);
  });
  setTimeout("refresh()",1000);
}

function selectTrack(id){
  $.post("/play/",{"selected":id},function(response){
    $("#status").text("Selected!");
  });
}

function deletePlaylist(id){
  $.post("/playlist/",{"id":id,"action":"delete"},function(response){
    $("#playlistLink").trigger("click");
  });
}

function editPlaylist(id,title){
  $("#titleInput").val(title);
  $("#titleInput").after("<input type='hidden' id='hiddenSelectedPlaylist' value='"+id+"' >")
  $("#modalPlaylist").modal('show');
  $("#closePlaylistEdition").on("touched click",function(e){
    var value = $("#hiddenSelectedPlaylist").val();
    var title = $("#titleInput").val();
    $.post("/playlist/",{"id":value,"action":"edit","title":title},function(){
      $("#playlistLink").trigger("click");
    });
    $("#hiddenSelectedPlaylist").remove();
  });
}

function selectPlaylist(id){
  $.post("/playlist/",{"id":id,"action":"select"},function(response){
    $("#currentPlaylistLink").trigger("click");
  });
}

$(document).ready(function(){

  $("#buttonImportPlaylist").on("touched click",function(){
    var url = $("#inputPlaylist").val();
    $.post("/playlist/",{"url":url,"action":"import","id":"none"},function(response){
      $("#playlistLink").trigger("click");
    });
  });

  $(".nav-link").on("touched click",function(e){
    $(".active").removeClass("active")
    $(this).parent().addClass("active");
    $("#status").text("Current is: "+$(this).text());
    var selected = $(this).attr("id");
    if(selected == 'currentPlaylistLink'){
      $("#rowPlaylist").addClass("d-none");
      $("#rowCurrentPlaylist").removeClass("d-none");
      $("#playlistFormDiv").removeClass("d-none");
      $("#importPlaylistFormDiv").addClass("d-none");
    }else if (selected == 'playlistLink'){
      $("#rowPlaylist").removeClass("d-none");
      $("#rowCurrentPlaylist").addClass("d-none");
      $("#playlistFormDiv").addClass("d-none");
      $("#importPlaylistFormDiv").removeClass("d-none");
      $("#playlistList").children().remove();
      $.post("/playlist/",{"id":"all"},function(response){
        var res = $.parseJSON(response);
        $.each(res.playlists,function(i,r){
          var edit = '<i onclick="editPlaylist(\''+r.id+'\',\''+r.name+'\')" ontouchend="editPlaylist(\''+r.id+'\',\''+r.name+'\')" class="far fa-edit" style="float:right;cursor:pointer;margin-right: 5px;"></i> ';
          var trash = ' <i onclick="deletePlaylist(\''+r.id+'\',\''+r.name+'\')" ontouchend="deletePlaylist(\''+r.id+'\',\''+r.name+'\')" class="fa fa-trash" aria-hidden="true" style="float:right;cursor:pointer;"></i>';
          var target = '<span onclick="selectPlaylist(\''+r.id+'\',\''+r.name+'\')" ontouchend="selectPlaylist(\''+r.id+'\',\''+r.name+'\')" style="cursor:pointer;">'+r.name+'</span>';
          var element = '<li class="list-group-item" >'+target+trash+edit+'</li>';
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
