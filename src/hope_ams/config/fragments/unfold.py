UNFOLD = {
    "SITE_TITLE": "Anomaly Management System",
    "SITE_HEADER": "AMS Admin",
    "SITE_URL": "/admin/",
    "SITE_SYMBOL": "shield",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": False,
    "COLORS": {
        "primary": {
            "50": "#edf4f6",
            "100": "#d3e6ed",
            "200": "#a9d3e3",
            "300": "#7bc3df",
            "400": "#48b5df",
            "500": "#1cabe2",
            "600": "#1f8cb6",
            "700": "#207292",
            "800": "#1e5970",
            "900": "#1a4150",
            "950": "#142d37",
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": "Overview",
                "items": [
                    {
                        "title": "Dashboard",
                        "icon": "dashboard",
                        "link": "/admin/",
                    },
                ],
            },
            {
                "title": "Detection",
                "items": [
                    {
                        "title": "Detection Runs",
                        "icon": "play_arrow",
                        "link": "/admin/hope_ams/detectionrun/",
                    },
                    {
                        "title": "Anomaly Results",
                        "icon": "warning",
                        "link": "/admin/hope_ams/anomalyresult/",
                    },
                ],
            },
            {
                "title": "Reference Data",
                "items": [
                    {
                        "title": "Offices",
                        "icon": "business",
                        "link": "/admin/hope_ams/office/",
                    },
                    {
                        "title": "Programmes",
                        "icon": "folder",
                        "link": "/admin/hope_ams/programme/",
                    },
                    {
                        "title": "Payment Plans",
                        "icon": "payments",
                        "link": "/admin/hope_ams/paymentplan/",
                    },
                ],
            },
            {
                "title": "Configuration",
                "items": [
                    {
                        "title": "Rule Configurations",
                        "icon": "tune",
                        "link": "/admin/hope_ams/ruleconfig/",
                    },
                    {
                        "title": "Programme Rule Configs",
                        "icon": "assignment",
                        "link": "/admin/hope_ams/programmeruleconfiguration/",
                    },
                ],
            },
        ],
    },
}
