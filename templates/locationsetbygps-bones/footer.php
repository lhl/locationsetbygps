      <footer class="footer" role="contentinfo">

        <div id="inner-footer" class="wrap cf">

          <nav role="navigation">
            <?php wp_nav_menu(array(
              'container' => '',                              // remove nav container
              'container_class' => 'footer-links cf',         // class of container (should you choose to use it)
              'menu' => __( 'Footer Links', 'bonestheme' ),   // nav name
              'menu_class' => 'nav footer-nav cf',            // adding custom nav class
              'theme_location' => 'footer-links',             // where it's located in the theme
              'before' => '',                                 // before the menu
              'after' => '',                                  // after the menu
              'link_before' => '',                            // before each link
              'link_after' => '',                             // after each link
              'depth' => 0,                                   // limit the depth of the nav
              'fallback_cb' => 'bones_footer_links_fallback'  // fallback function
            )); ?>
          </nav>

          <p class="source-org copyright">&copy; <?php echo date('Y'); ?> <?php bloginfo( 'name' ); ?>.</p>

        </div>

      </footer>

    </div>

    <?php // all js scripts are loaded in library/bones.php ?>
    <?php wp_footer(); ?>

<script>
(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
})(window,document,'script','//www.google-analytics.com/analytics.js','ga');
ga('create', 'UA-53604204-1', 'auto');
ga('send', 'pageview');
</script>

  </body>

</html>
