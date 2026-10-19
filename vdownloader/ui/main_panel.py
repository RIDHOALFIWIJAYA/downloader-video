from types import SimpleNamespace

import customtkinter as ctk


def build_main_panel(parent, *, download_path_var, on_fetch, on_add, on_remove,
                     on_download, on_cancel):
    main_frame = ctk.CTkFrame(parent, fg_color="transparent")
    main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

    url_label = ctk.CTkLabel(main_frame, text="URL Video / YouTube (Auto-detect active)",
                             font=ctk.CTkFont(size=13))
    url_label.pack(anchor="w", pady=(0, 5))

    url_entry = ctk.CTkEntry(main_frame, placeholder_text="Paste link from browser...",
                             placeholder_text_color=("#606060", "#94a3b8"), height=35)
    url_entry.pack(fill="x", pady=(0, 10))
    url_entry.bind("<Return>", lambda e: on_fetch())

    q_btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    q_btn_frame.pack(fill="x", pady=5)

    btn_add = ctk.CTkButton(q_btn_frame, text="+ Add to Queue", command=on_add, width=155)
    btn_add.pack(side="left")

    btn_del = ctk.CTkButton(q_btn_frame, text="🗑️ Remove Last", command=on_remove,
                            fg_color="#ef4444", hover_color="#dc2626", width=120)
    btn_del.pack(side="left", padx=10)

    queue_list = ctk.CTkTextbox(main_frame, height=120, fg_color="#0f172a",
                                text_color="#94a3b8")
    queue_list.pack(fill="x", pady=10)

    info_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    info_frame.pack(fill="x", pady=10)

    quality_box = ctk.CTkComboBox(
        info_frame,
        values=["Best Quality", "720p (MP4)", "480p (MP4)", "Audio Only (MP3)"],
        width=200,
    )
    quality_box.set("Best Quality")
    quality_box.pack(side="left")

    path_display = ctk.CTkLabel(info_frame, textvariable=download_path_var,
                                text_color="#64748b", font=ctk.CTkFont(size=11),
                                wraplength=350)
    path_display.pack(side="left", padx=20)

    info_label = ctk.CTkLabel(main_frame, text="Title: ...",
                              font=ctk.CTkFont(size=12, weight="bold"),
                              text_color="#38bdf8", wraplength=600, justify="left")
    info_label.pack(anchor="w", pady=(20, 5))

    progress_bar = ctk.CTkProgressBar(main_frame, orientation="horizontal")
    progress_bar.set(0)
    progress_bar.pack(fill="x", pady=10)

    status_label = ctk.CTkLabel(main_frame, text="Status: Idle", text_color="#4ade80")
    status_label.pack()

    btn_download = ctk.CTkButton(main_frame, text="Start Download", command=on_download,
                                 height=50, font=ctk.CTkFont(size=14, weight="bold"),
                                 fg_color=("#0ea5e9", "#1f6aa5"), hover_color="#0284c7")
    btn_download.pack(fill="x", pady=(20, 5))

    btn_cancel = ctk.CTkButton(main_frame, text="Cancel Download", command=on_cancel,
                               height=35, fg_color="#ef4444", hover_color="#dc2626",
                               state="disabled")
    btn_cancel.pack(fill="x", pady=(0, 10))

    return SimpleNamespace(
        main_frame=main_frame,
        url_entry=url_entry,
        btn_add=btn_add,
        btn_del=btn_del,
        queue_list=queue_list,
        quality_box=quality_box,
        path_display=path_display,
        info_label=info_label,
        progress_bar=progress_bar,
        status_label=status_label,
        btn_download=btn_download,
        btn_cancel=btn_cancel,
    )
