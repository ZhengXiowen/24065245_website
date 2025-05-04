$(function() {
    $('.book-card').hover(
        function() {
            var card = $(this);
            var bookId = card.data('id');
            $.getJSON('/api/book/' + bookId, function(data) {
                var envLabel = (typeof currentLang !== 'undefined' && currentLang === 'zh') ? '环境影响' : 'Env Impact';
                var content = '<h5>' + data.name + '</h5><p>' + data.description + '</p><p>' + envLabel + ': ' + data.env + '</p>';
        
                $('#hover-detail-box').html(content).css({
                    position: 'absolute',
                    top: card.offset().top + 'px',
                    left: (card.offset().left + card.outerWidth() + 10) + 'px',
                    background: '#F8F5F0',
                    border: '1px solid #BEB1A8',
                    padding: '10px',
                    width: '250px',
                    boxShadow: '0 0 10px rgba(0,0,0,0.2)',
                    zIndex: 1000
                }).show();
            });
        },
        function() {
            $('#hover-detail-box').hide();
        }
    );
});
