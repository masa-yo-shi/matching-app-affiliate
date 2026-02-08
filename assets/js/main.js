/**
 * マッチングアプリアフィリエイトサイト - メインJavaScript
 */

(function() {
  'use strict';

  /**
   * スムーズスクロール
   */
  function initSmoothScroll() {
    const links = document.querySelectorAll('a[href^="#"]');

    links.forEach(link => {
      link.addEventListener('click', function(e) {
        const href = this.getAttribute('href');
        if (href === '#') return;

        const target = document.querySelector(href);
        if (target) {
          e.preventDefault();
          target.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
          });
        }
      });
    });
  }

  /**
   * 外部リンクに target="_blank" を追加
   */
  function initExternalLinks() {
    const links = document.querySelectorAll('a[href^="http"]');

    links.forEach(link => {
      const href = link.getAttribute('href');
      if (href && !href.includes(window.location.hostname)) {
        link.setAttribute('target', '_blank');
        link.setAttribute('rel', 'noopener noreferrer');
      }
    });
  }

  /**
   * 画像の遅延読み込み
   */
  function initLazyLoading() {
    if ('loading' in HTMLImageElement.prototype) {
      // ブラウザがネイティブの遅延読み込みをサポートしている場合
      const images = document.querySelectorAll('img[loading="lazy"]');
      images.forEach(img => {
        img.src = img.dataset.src || img.src;
      });
    } else {
      // フォールバック: Intersection Observer
      const images = document.querySelectorAll('img[loading="lazy"]');

      const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            const img = entry.target;
            img.src = img.dataset.src || img.src;
            img.removeAttribute('loading');
            observer.unobserve(img);
          }
        });
      });

      images.forEach(img => imageObserver.observe(img));
    }
  }

  /**
   * 目次の自動生成 (オプション)
   */
  function generateTableOfContents() {
    const tocContainer = document.querySelector('#table-of-contents');
    if (!tocContainer) return;

    const headings = document.querySelectorAll('.post-content h2, .post-content h3');
    if (headings.length === 0) return;

    const toc = document.createElement('ul');
    toc.className = 'toc-list';

    headings.forEach((heading, index) => {
      const id = heading.id || `heading-${index}`;
      heading.id = id;

      const li = document.createElement('li');
      li.className = heading.tagName.toLowerCase() === 'h3' ? 'toc-item-sub' : 'toc-item';

      const link = document.createElement('a');
      link.href = `#${id}`;
      link.textContent = heading.textContent;

      li.appendChild(link);
      toc.appendChild(li);
    });

    tocContainer.appendChild(toc);
  }

  /**
   * アフィリエイトリンククリック追跡 (オプション)
   */
  function trackAffiliateClicks() {
    const affiliateLinks = document.querySelectorAll('a[href*="affiliate"]');

    affiliateLinks.forEach(link => {
      link.addEventListener('click', function() {
        const url = this.getAttribute('href');
        // Google Analytics やその他の分析ツールにイベントを送信
        if (typeof gtag !== 'undefined') {
          gtag('event', 'click', {
            event_category: 'affiliate',
            event_label: url,
            value: 1
          });
        }
      });
    });
  }

  /**
   * 初期化
   */
  function init() {
    initSmoothScroll();
    initExternalLinks();
    initLazyLoading();
    generateTableOfContents();
    trackAffiliateClicks();
  }

  // DOMContentLoaded時に初期化
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
