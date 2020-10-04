$(document).ready(function () {

  $("#analyseBTN").prop("disabled", true);

  $("#btnSubmit").click(function (event) {
    $("#upload-load").css("display", "block");
    //stop submit the form, we will post it manually.
    event.preventDefault();

    // Get form
    var form = $('#fileUploadForm')[0];
    var data = new FormData(form);

    $("#btnSubmit").prop("disabled", true);

    $.ajax({
      type: "POST",
      enctype: 'multipart/form-data',
      url: "http://127.0.0.1:5000/upload",
      data: data,
      processData: false,
      contentType: false,
      cache: false,
      timeout: 600000,
      success: function (data) {
        $("#result").text("(\"" + data.file_path + "\")");
        $("#btnSubmit").prop("disabled", false);
        $("#upload-load").css("display", "none");
        $("#analyseBTN").prop("disabled", false);
      },
      error: function (e) {
        $("#result").text(e.responseText);
        console.log("ERROR : ", e);
        $("#btnSubmit").prop("disabled", false);
        $("#upload-load").css("display", "none");
      }
    });
  });

  $("#analyseBTN").click(function (event) {
    $("#analyse-load").css("display", "block");
    $("#analyseBTN").prop("disabled", true);

    $.ajax({
      type: "GET",
      dataType: "json",
      url: "http://127.0.0.1:5000/predict/" + $("#result").text().slice(2, length - 2),
      success: function (data) {
        var result = data.result;
        var incorrect_entries = data.incorrect_entries;
        var headers = data.result[0].Header;
        table = '<table class="table striped centered"><thead>';
        incorrect_entries_table = '<table class="table striped centered"><thead>';
        for (let i = 0; i < headers.length; i++) {
          table += '<th>' + headers[i] + '</th>';
          incorrect_entries_table += '<th>' + headers[i] + '</th>';
        }
        incorrect_entries_table += '<th> Reason </th> </thead><tbody>';
        table += '</thead><tbody>'
        for (let i = 1; i < result.length; i++) {
          var values = result[i].values;
          table += '<tr>'
          for (let j = 0; j < values.length; j++) {
            table += '<td>' + values[j] + '</td>';
          }
          table += '</tr>'
        }

        for (let i = 0; i < incorrect_entries.length; i++) {
          var values = incorrect_entries[i].values;
          incorrect_entries_table += '<tr>'
          for (let j = 0; j < values.length; j++) {
            incorrect_entries_table += '<td>' + values[j] + '</td>';
          }
          incorrect_entries_table += '<td>' + incorrect_entries[i].error + '</td></tr>'
        }
        incorrect_entries_table += '</tbody></table>';
        table += '</tbody></table>';
        document.getElementById("analysedResult").innerHTML = table;
        
        if (incorrect_entries.length > 0) {
          $("#incorrect-entries-container").css("display", "block");
          document.getElementById("incorrect-entries").innerHTML = incorrect_entries_table;
        }

        $("#analysed-result").css("display", "block");
        $("#video").css("background-color", "#072540");
        $("#team").css("background-color", "#183d5d");
        $("#analyse-load").css("display", "none");
        $("#analyseBTN").prop("disabled", false);
      },
      error: function (error) {
        jsonValue = jQuery.parseJSON(error.responseText);
        alert(jsonValue.message);
        $("#analyse-load").css("display", "none");
        $("#analyseBTN").prop("disabled", false);
      }
    });

  });

  $('.parallax').parallax();
});
