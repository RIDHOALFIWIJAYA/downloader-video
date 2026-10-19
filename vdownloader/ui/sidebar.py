from types import SimpleNamespace

import customtkinter as ctk


def build_sidebar(parent, *, download_path_var, platform_text, on_browse,
                  on_open_folder, on_history, on_theme):
    sidebar = ctk.CTkFrame(parent, width=210, corner_radius=0)
    sidebar.grid(row=0, column=0, sticky="nsew")

    logo = ctk.CTkLabel(sidebar, text="V-DL v5.4", text_color="#87CEEB",
                        font=ctk.CTkFont(size=25, weight="bold"), fg_color="#334155",
                        corner_radius=14)
    logo.pack(pady=30, padx=15)

    thumb_label = ctk.CTkLabel(sidebar, text="Thumbnail...", text_color="#87CEEB",
                               width=200, height=120, fg_color="#0f172a", corner_radius=8)
    thumb_label.pack(pady=10, padx=20)

    size_label = ctk.CTkLabel(sidebar, text="Size: -", font=ctk.CTkFont(size=12))
    size_label.pack(pady=2)
    duration_label = ctk.CTkLabel(sidebar, text="Duration: -", font=ctk.CTkFont(size=12))
    duration_label.pack(pady=2)

    btn_browse = ctk.CTkButton(sidebar, text="📁 Choose Folder", command=on_browse,
                               fg_color="#334155")
    btn_browse.pack(pady=10, padx=20)

    btn_open = ctk.CTkButton(sidebar, text="📂 Open Folder", command=on_open_folder,
                             fg_color="transparent", border_width=1)
    btn_open.pack(pady=10, padx=20)

    btn_history = ctk.CTkButton(sidebar, text="📜 View History", command=on_history,
                                fg_color="#1e293b", hover_color="#334155")
    btn_history.pack(pady=10, padx=20)

    theme_label = ctk.CTkLabel(sidebar, text="Appearance Mode:", font=ctk.CTkFont(size=11))
    theme_label.pack(pady=(20, 0))
    theme_option = ctk.CTkOptionMenu(sidebar, values=["Dark", "Light", "System"],
                                     command=on_theme)
    theme_option.set("Dark")
    theme_option.pack(pady=10, padx=20)

    platform_label = ctk.CTkLabel(sidebar, text=platform_text, font=ctk.CTkFont(size=10),
                                  text_color="#4ade80")
    platform_label.pack(side="bottom", pady=20)

    return SimpleNamespace(
        sidebar=sidebar,
        logo=logo,
        thumb_label=thumb_label,
        size_label=size_label,
        duration_label=duration_label,
        btn_browse=btn_browse,
        btn_open=btn_open,
        btn_history=btn_history,
        theme_option=theme_option,
        platform_label=platform_label,
    )
