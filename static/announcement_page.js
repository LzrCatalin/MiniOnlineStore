document.addEventListener('DOMContentLoaded', function () {
  // Get the modal
  const modal = document.getElementById('imageModal');

  // Get the image and insert it inside the modal
  const images = document.querySelectorAll('.announcement-image img');
  const modalImg = document.getElementById('expandedImg');
  images.forEach((img) => {
      img.addEventListener('click', function () {
          modal.style.display = 'block';
          modalImg.src = this.src;
      });
  });

  // Get the <span> element that closes the modal
  const closeSpan = document.querySelector('.close');

  // When the user clicks on <span> (x), close the modal
  closeSpan.addEventListener('click', function () {
      modal.style.display = 'none';
  });
});
