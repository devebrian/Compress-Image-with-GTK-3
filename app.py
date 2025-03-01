import os
import gi
from PIL import Image
import piexif

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib

class ExifRemoverApp(Gtk.Window):
    def __init__(self):
        super().__init__(title="Remove EXIF & Compress Images")
        self.set_default_size(400, 250)

        # Main layout
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox.set_margin_top(10)
        vbox.set_margin_bottom(10)
        vbox.set_margin_start(10)
        vbox.set_margin_end(10)

        # Select input folder button
        self.input_label = Gtk.Label(label="Input Folder: Not selected")
        self.btn_input = Gtk.Button(label="Select Input Folder")
        self.btn_input.connect("clicked", self.select_input_folder)

        # Select output folder button
        self.output_label = Gtk.Label(label="Output Folder: Not selected")
        self.btn_output = Gtk.Button(label="Select Output Folder")
        self.btn_output.connect("clicked", self.select_output_folder)

        # Compression quality slider
        self.quality_label = Gtk.Label(label="Quality: 85%")
        self.quality_adjustment = Gtk.Adjustment(85, 10, 100, 1, 10, 0)
        self.quality_slider = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=self.quality_adjustment)
        self.quality_slider.set_value_pos(Gtk.PositionType.RIGHT)
        self.quality_slider.connect("value-changed", self.update_quality)

        # Progress label
        self.progress_label = Gtk.Label(label="Progress: 0 images processed")

        # Start processing button
        self.btn_start = Gtk.Button(label="Start Processing")
        self.btn_start.connect("clicked", self.process_images)

        # Add widgets to layout
        vbox.pack_start(self.input_label, False, False, 0)
        vbox.pack_start(self.btn_input, False, False, 0)
        vbox.pack_start(self.output_label, False, False, 0)
        vbox.pack_start(self.btn_output, False, False, 0)
        vbox.pack_start(self.quality_label, False, False, 0)
        vbox.pack_start(self.quality_slider, False, False, 0)
        vbox.pack_start(self.progress_label, False, False, 0)
        vbox.pack_start(self.btn_start, False, False, 0)

        self.add(vbox)

        # Variables to store folder paths
        self.input_folder = ""
        self.output_folder = ""

    def select_input_folder(self, widget):
        dialog = Gtk.FileChooserDialog(
            title="Select Input Folder", parent=self, action=Gtk.FileChooserAction.SELECT_FOLDER
        )
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK)

        if dialog.run() == Gtk.ResponseType.OK:
            self.input_folder = dialog.get_filename()
            self.input_label.set_text(f"Input Folder: {self.input_folder}")

        dialog.destroy()

    def select_output_folder(self, widget):
        dialog = Gtk.FileChooserDialog(
            title="Select Output Folder", parent=self, action=Gtk.FileChooserAction.SELECT_FOLDER
        )
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK)

        if dialog.run() == Gtk.ResponseType.OK:
            self.output_folder = dialog.get_filename()
            self.output_label.set_text(f"Output Folder: {self.output_folder}")

        dialog.destroy()

    def update_quality(self, widget):
        quality = int(self.quality_slider.get_value())
        self.quality_label.set_text(f"Quality: {quality}%")

    def process_images(self, widget):
        if not self.input_folder or not self.output_folder:
            self.input_label.set_text("⚠ Select an input folder first!")
            self.output_label.set_text("⚠ Select an output folder first!")
            return

        quality = int(self.quality_slider.get_value())
        os.makedirs(self.output_folder, exist_ok=True)

        file_list = [f for f in os.listdir(self.input_folder) if f.lower().endswith((".jpg", ".jpeg"))]
        total_files = len(file_list)

        if total_files == 0:
            self.progress_label.set_text("No image files found in input folder.")
            return

        processed_count = 0
        for filename in file_list:
            input_path = os.path.join(self.input_folder, filename)
            output_path = os.path.join(self.output_folder, filename)

            try:
                image = Image.open(input_path)
                image.save(output_path, "jpeg", quality=quality, optimize=True, exif=b"")
                processed_count += 1
                self.progress_label.set_text(f"Progress: {processed_count}/{total_files} images processed")

                # Force UI update (since Gtk is synchronous)
                while Gtk.events_pending():
                    Gtk.main_iteration()

            except Exception as e:
                print(f"Failed to process {filename}: {e}")

        # Reset folder paths after processing is complete
        self.input_folder = ""
        self.output_folder = ""
        self.input_label.set_text("Input Folder: Not selected")
        self.output_label.set_text("Output Folder: Not selected")

        self.btn_start.set_label("✔ Done!")
        self.progress_label.set_text(f"Processing complete! {processed_count} images processed.")

if __name__ == "__main__":
    app = ExifRemoverApp()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main()
