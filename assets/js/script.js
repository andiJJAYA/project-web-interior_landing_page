document.addEventListener('DOMContentLoaded', function() {
    // 1. Dapatkan elemen navbar collapse (menu yang muncul)
    var navCollapse = document.getElementById('navMenu');

    // Pastikan elemen tersebut ada
    if (navCollapse) {
        // Buat objek Collapse dari Bootstrap untuk mengontrolnya
        var bsCollapse = new bootstrap.Collapse(navCollapse, {
            toggle: false // Jangan toggle secara otomatis saat inisialisasi
        });

        // 2. Dapatkan semua tautan navigasi di dalam menu
        var navLinks = navCollapse.querySelectorAll('.nav-link');

        // 3. Iterasi setiap tautan dan tambahkan event listener
        navLinks.forEach(function(link) {
            link.addEventListener('click', function() {
                // Periksa apakah menu sedang terbuka (kelas 'show')
                if (navCollapse.classList.contains('show')) {
                    // Jika menu terbuka, panggil metode hide() dari Bootstrap Collapse
                    bsCollapse.hide();
                }
            });
        });
    }
});