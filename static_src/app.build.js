({
    appDir: ".",
    baseUrl: "js",
    dir: "../static",
    paths: {
        bootstrap: 'lib/bootstrap.min',
        jquery: 'lib/jquery.min',
        lodash: 'lib/lodash.min',
        backbone: 'lib/backbone-min',
    },


    shim: {
        'backbone': {
            deps: ['jquery', 'lodash'],
            exports: 'Backbone',
        },
        'bootstrap' : ['jquery']
    },

    modules: [
        {
            name: "main"
        }
    ]
})