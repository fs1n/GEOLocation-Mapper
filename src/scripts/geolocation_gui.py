import flet as ft
import random
from datetime import datetime

class GeolocationApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Geolocation Analytics Suite"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 20
        self._setup_ui()
        
    def _setup_ui(self):
        # Navigation Rail
        self.nav_rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            destinations=[
                ft.NavigationRailDestination(icon=ft.icons.DASHBOARD, label="Dashboard"),
                ft.NavigationRailDestination(icon=ft.icons.MAP, label="Map View"),
                ft.NavigationRailDestination(icon=ft.icons.PEOPLE, label="Profiles"),
                ft.NavigationRailDestination(icon=ft.icons.SETTINGS, label="Settings"),
            ],
            on_change=self._switch_view,
        )

        # Main Content Area
        self.content_area = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True)
        
        # Assemble Layout
        self.page.add(
            ft.Row(
                [
                    self.nav_rail,
                    ft.VerticalDivider(width=1),
                    self.content_area,
                ],
                expand=True,
            )
        )
        
        # Initial View
        self._show_dashboard()

    def _switch_view(self, e):
        view_index = self.nav_rail.selected_index
        self.content_area.controls.clear()
        
        if view_index == 0:
            self._show_dashboard()
        elif view_index == 1:
            self._show_map_view()
        elif view_index == 2:
            self._show_profiles()
        elif view_index == 3:
            self._show_settings()
            
        self.page.update()

    def _show_dashboard(self):
        # Metrics Cards
        metrics = ft.Row(
            controls=[
                self._create_metric_card("Total Profiles", "1,234", ft.icons.PEOPLE, "#4CAF50"),
                self._create_metric_card("Active Devices", "892", ft.icons.PHONE_ANDROID, "#2196F3"),
                self._create_metric_card("Locations Today", "15,678", ft.icons.EXPLORE, "#FF9800"),
            ],
            spacing=20
        )
        
        # Recent Activity
        activity_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Time")),
                ft.DataColumn(ft.Text("Device")),
                ft.DataColumn(ft.Text("Location")),
            ],
            rows=[
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text("12:34 PM")),
                        ft.DataCell(ft.Text("Device #123")),
                        ft.DataCell(ft.Text(f"{random.uniform(-90, 90):.4f}, {random.uniform(-180, 180):.4f}")),
                    ]
                ) for _ in range(5)
            ]
        )
        
        self.content_area.controls.extend([
            ft.Text("Dashboard", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
            metrics,
            ft.Divider(),
            ft.Text("Recent Activity", style=ft.TextThemeStyle.HEADLINE_SMALL),
            activity_table
        ])
        
    def _show_map_view(self):
        # Map Container
        map_container = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Dropdown(
                        options=[
                            ft.dropdown.Option("Heatmap"),
                            ft.dropdown.Option("Path Visualization"),
                            ft.dropdown.Option("Cluster View"),
                        ],
                        value="Heatmap",
                        width=200
                    ),
                    ft.ElevatedButton("Refresh Data", icon=ft.icons.REFRESH)
                ]),
                ft.Container(
                    content=ft.Text("Map Integration Area", size=20),
                    border=ft.border.all(1, ft.colors.GREY_400),
                    border_radius=10,
                    padding=20,
                    height=500,
                    alignment=ft.alignment.center
                )
            ]),
        )
        
        self.content_area.controls.extend([
            ft.Text("Geospatial Analysis", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
            map_container
        ])

    def _show_profiles(self):
        # Profile Data Table
        profiles_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Name")),
                ft.DataColumn(ft.Text("Email")),
                ft.DataColumn(ft.Text("Devices")),
                ft.DataColumn(ft.Text("Actions")),
            ],
            rows=[
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text("123")),
                        ft.DataCell(ft.Text("John Doe")),
                        ft.DataCell(ft.Text("john@example.com")),
                        ft.DataCell(ft.Text("3")),
                        ft.DataCell(
                            ft.Row([
                                ft.IconButton(ft.icons.EDIT, tooltip="Edit"),
                                ft.IconButton(ft.icons.DELETE, tooltip="Delete"),
                            ])
                        ),
                    ]
                ) for _ in range(10)
            ]
        )
        
        # Add Profile Dialog
        def close_dlg(e):
            add_profile_dialog.open = False
            self.page.update()

        def save_profile(e):
            # Add validation and save logic
            close_dlg(e)

        add_profile_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Add New Profile"),
            content=ft.Column([
                ft.TextField(label="Full Name"),
                ft.TextField(label="Email"),
                ft.Dropdown(label="Primary Device", options=[
                    ft.dropdown.Option(f"Device #{i}") for i in range(1, 6)
                ])
            ]),
            actions=[
                ft.TextButton("Cancel", on_click=close_dlg),
                ft.TextButton("Save", on_click=save_profile),
            ]
        )

        def open_dlg(e):
            self.page.dialog = add_profile_dialog
            add_profile_dialog.open = True
            self.page.update()

        self.content_area.controls.extend([
            ft.Row([
                ft.Text("Profile Management", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
                ft.ElevatedButton("Add Profile", icon=ft.icons.ADD, on_click=open_dlg)
            ]),
            profiles_table
        ])

    def _show_settings(self):
        settings_content = ft.Column([
            ft.Switch(label="Enable Real-time Updates", value=True),
            ft.Dropdown(
                label="Map Provider",
                options=[
                    ft.dropdown.Option("OpenStreetMap"),
                    ft.dropdown.Option("Google Maps"),
                    ft.dropdown.Option("Mapbox"),
                ],
                value="OpenStreetMap"
            ),
            ft.Slider(
                label="Cache Duration (hours)",
                min=1,
                max=24,
                divisions=23,
                value=6
            ),
            ft.ElevatedButton("Save Settings", icon=ft.icons.SAVE)
        ])
        
        self.content_area.controls.extend([
            ft.Text("Application Settings", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
            settings_content
        ])

    def _create_metric_card(self, title: str, value: str, icon, color: str):
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Icon(icon, color=color, size=40),
                    ft.Text(value, style=ft.TextThemeStyle.HEADLINE_LARGE),
                    ft.Text(title, style=ft.TextThemeStyle.BODY_MEDIUM),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=20,
                width=200,
                height=150,
            )
        )

def main(page: ft.Page):
    GeolocationApp(page)

ft.app(target=main, view=ft.WEB_BROWSER)