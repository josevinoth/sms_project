/**
 * Desktop Table Horizontal Scroll Helper
 * Provides a clean sticky floating horizontal scrollbar at the bottom of the screen
 * whenever wide tables overflow vertically beyond the viewport.
 */
(function ($) {
    'use strict';

    function attachScrollHelper(containerEl) {
        var $container = $(containerEl);
        if ($container.data('table-scroll-attached')) return;

        // Ensure container can scroll horizontally
        var style = window.getComputedStyle(containerEl);
        var overflowX = style.getPropertyValue('overflow-x');
        if (overflowX !== 'auto' && overflowX !== 'scroll') {
            $container.css('overflow-x', 'auto');
        }

        $container.data('table-scroll-attached', true);

        // STICKY BOTTOM Viewport Scrollbar (clean horizontal scrollbar fixed at bottom of screen, no arrows)
        var $stickyBar = $('<div class="sticky-table-scrollbar-wrapper">' +
            '<div class="sticky-table-scrollbar-inner"><div class="sticky-table-scrollbar-content"></div></div>' +
            '</div>');

        $('body').append($stickyBar);

        var $stickyInner = $stickyBar.find('.sticky-table-scrollbar-inner');
        var $stickyContent = $stickyBar.find('.sticky-table-scrollbar-content');
        var stickyInnerEl = $stickyInner[0];

        // State lock to prevent infinite scroll loop
        var syncLock = false;
        var $dtHeader = $container.siblings('.dataTables_scrollHead');

        function setAllScrollLeft(val, source) {
            if (syncLock) return;
            syncLock = true;

            if (source !== 'container') containerEl.scrollLeft = val;
            if (source !== 'sticky') stickyInnerEl.scrollLeft = val;

            // If DataTables with scrollX, sync header container as well
            if ($dtHeader.length && source !== 'header') {
                $dtHeader[0].scrollLeft = val;
            }

            syncLock = false;
        }

        // Scroll synchronization handlers
        $container.on('scroll.tableScrollHelper', function () {
            setAllScrollLeft(containerEl.scrollLeft, 'container');
        });

        $stickyInner.on('scroll.tableScrollHelper', function () {
            setAllScrollLeft(stickyInnerEl.scrollLeft, 'sticky');
        });

        if ($dtHeader.length) {
            $dtHeader.on('scroll.tableScrollHelper', function () {
                setAllScrollLeft(this.scrollLeft, 'header');
            });
            $dtHeader.on('wheel.tableScrollHelper', function (e) {
                var evt = e.originalEvent || e;
                var delta = evt.deltaY || evt.deltaX;
                if (evt.shiftKey || Math.abs(evt.deltaX) > Math.abs(evt.deltaY)) {
                    containerEl.scrollLeft += delta;
                    e.preventDefault();
                }
            });
        }

        // Mouse Wheel Horizontal Scroll
        $container.on('wheel.tableScrollHelper', function (e) {
            var evt = e.originalEvent || e;
            var delta = evt.deltaY || evt.deltaX;
            if (evt.shiftKey || Math.abs(evt.deltaX) > Math.abs(evt.deltaY)) {
                containerEl.scrollLeft += delta;
                e.preventDefault();
            }
        });

        // Global DataTables configuration: disable responsive column collapse, force horizontal scrollbar
        if ($.fn && $.fn.dataTable) {
            $.extend(true, $.fn.dataTable.defaults, {
                responsive: false,
                scrollX: true,
                autoWidth: true
            });
        }

        // Update scrollbar dimensions and position
        function updateLayout() {
            var scrollWidth = containerEl.scrollWidth;
            var clientWidth = containerEl.clientWidth;
            var hasOverflow = scrollWidth > clientWidth + 5;

            if (!hasOverflow) {
                $stickyBar.hide();
                return;
            }

            var rect = containerEl.getBoundingClientRect();
            var windowHeight = $(window).height();

            var isTopVisibleOrAbove = rect.top < windowHeight;
            var isBottomBelowViewport = rect.bottom > windowHeight + 20;

            if (isTopVisibleOrAbove && isBottomBelowViewport) {
                $stickyContent.css('width', scrollWidth + 'px');
                $stickyBar.css({
                    left: rect.left + 'px',
                    width: clientWidth + 'px',
                    display: 'block'
                });
                stickyInnerEl.scrollLeft = containerEl.scrollLeft;
            } else {
                $stickyBar.hide();
            }
        }

        $(window).on('scroll.tableScrollHelper resize.tableScrollHelper', updateLayout);
        updateLayout();

        $container.data('updateLayout', updateLayout);
    }

    function scanAndAttach() {
        // Priority 1: DataTables scroll bodies (these are the true scrolling containers for DataTables)
        $('.dataTables_scrollBody').each(function () {
            attachScrollHelper(this);
            var update = $(this).data('updateLayout');
            if (update) update();
        });

        // Priority 2: Standalone responsive tables (tables without DataTables scrollX)
        $('.table-responsive, .shadow-box-table').each(function () {
            // Do not attach to outer container if it wraps a DataTables scroll structure
            if ($(this).find('.dataTables_scrollBody').length === 0 && $(this).closest('.dataTables_scroll').length === 0) {
                attachScrollHelper(this);
                var update = $(this).data('updateLayout');
                if (update) update();
            }
        });
    }

    // Keyboard Left/Right Arrow Navigation
    $(document).on('keydown', function (e) {
        if (e.shiftKey && (e.which === 37 || e.which === 39)) {
            var $activeContainer = $('.dataTables_scrollBody, .table-container-modern, .table-responsive').filter(':visible').first();
            if ($activeContainer.length) {
                var current = $activeContainer.scrollLeft();
                var step = e.which === 37 ? -250 : 250;
                $activeContainer.stop().animate({ scrollLeft: current + step }, 150);
                e.preventDefault();
            }
        }
    });

    function adjustAllDtColumns() {
        if ($.fn && $.fn.dataTable) {
            $.fn.dataTable.tables({ visible: true, api: true }).columns.adjust();
        }
    }

    $(document).ready(function () {
        scanAndAttach();
        adjustAllDtColumns();

        $(document).on('draw.dt init.dt xhr.dt', function () {
            setTimeout(function () {
                scanAndAttach();
                adjustAllDtColumns();
            }, 50);
            setTimeout(function () {
                scanAndAttach();
                adjustAllDtColumns();
            }, 250);
        });

        $(window).on('resize.dtAdjust', function () {
            adjustAllDtColumns();
        });

        setInterval(scanAndAttach, 1000);
    });

    window.initTableScrollHelper = scanAndAttach;

})(jQuery);
