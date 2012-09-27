$(document).ready(function () {
	$("#helpButton").click(function () {
			// check visibility
			if ($("#helpMenu").is(":hidden")) {
				// it's hidden - show it
				$("#helpMenu").slideDown("normal");
				$(this).removeClass("ui-state-focus");
			} else {
					// it's not hidden - slide it down
					$("#helpMenu").slideUp("normal");
					$(this).removeClass("ui-state-focus");
			}
	});
});

