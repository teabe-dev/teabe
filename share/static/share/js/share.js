$(document).ready(function () {
    // 偵測url並標記點擊
    // $("a[href='" + window.location.pathname + "']").addClass("active");

    share_resize()
});

$(window).resize(share_resize);

function share_resize() {
    var wdth = $(window).width();
    var mark = sessionStorage.getItem("mark-LR");
    console.log(mark)
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

function set_modal_content(member_id) {
    $.get(`/share/modal_group_members/${member_id}/`, function (data) {
        $("#modal_content").html(data);
    });
}