/*
Implementation alert in case user wants to add announcement
but it is not logged in. After message, user is move
to login page
*/
function showAlert() {
	alert("Please log in to add an announcement!");
	window.location.href = "/login";
}
