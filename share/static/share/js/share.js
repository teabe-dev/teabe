$(document).ready(function () {
    // 偵測url並標記點擊
    // $("a[href='" + window.location.pathname + "']").addClass("active");

    share_resize()
});

$(window).resize(share_resize);

function share_resize() {
    var wdth = $(window).width();
    var mark = sessionStorage.getItem("mark-LR");
    if (wdth < 768) {
        // 看標記點顯示左還是右
        if (mark == 'L' | mark == null) {
            $(".left-div").show();
            $(".right-div").hide();
        } else {
            $(".left-div").hide();
            $(".right-div").show();
        }

    } else {
        // 歸位兩邊都顯示
        $(".left-div").show();
        $(".right-div").show();
    }
}

$(".left-button").click(function () {
    // 左邊按鈕 點擊顯示右邊
    // event.preventDefault() // 取消預設的行為
    // var width = $(window).width();
    // if (width < 768) {
    //   $(".left-div").hide()
    //   $(".right-div").show();
    // }
    sessionStorage.setItem("mark-LR", "R");

});

$(".right-button").click(function () {
    // 右邊按鈕點擊 顯示左邊
    var width = $(window).width();
    if (width < 768) {
        $(".right-div").hide()
        $(".left-div").show();
        sessionStorage.setItem("mark-LR", "L");
    }
});

function text_to_copy(text) {
    // https可用，http會報錯Uncaught TypeError: Cannot read properties of undefined (reading 'writeText')
    navigator.clipboard.writeText(text).then(function () {
        console.log('複製成功');
    }, function (err) {
        console.error('複製失敗: ', err);
    });
}

function set_modal_content(page) {
    $.get(`/share/${page}/`, function (data) {
        $("#modal_content").html(data);
    });
}


var language = {
    "processing": "處理中...",
    "loadingRecords": "載入中...",
    "lengthMenu": "顯示 _MENU_ 項結果",
    "zeroRecords": "沒有符合的結果",
    "info": "顯示第 _START_ 至 _END_ 項結果，共 _TOTAL_ 項",
    "infoEmpty": "顯示第 0 至 0 項結果，共 0 項",
    "infoFiltered": "(從 _MAX_ 項結果中過濾)",
    "infoPostFix": "",
    "search": "搜尋:",
    "paginate": {
        "first": "第一頁",
        "previous": "上一頁",
        "next": "下一頁",
        "last": "最後一頁"
    },
    "aria": {
        "sortAscending": ": 升冪排列",
        "sortDescending": ": 降冪排列"
    }
}
