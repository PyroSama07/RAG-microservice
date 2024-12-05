import gradio as gr
import os

class ChatbotInterface:
    def __init__(self):
        self.uploaded_files = []
        self.notification_box = None

    def upload_file(self, file):
        # if file is not None:
        #     filename = os.path.basename(file.name)
        #     if filename not in self.uploaded_files:
        #         self.uploaded_files.append(filename)
        #         self.show_notification("File uploaded successfully!")
        #         return gr.update(value=self.uploaded_files)
        self.show_notification("File upload failed.")
        return gr.update(value=self.uploaded_files)

    def delete_file(self, filename):
        # if filename in self.uploaded_files:
        #     self.uploaded_files.remove(filename)
        #     self.show_notification(f"Deleted file: {filename}")
        #     return gr.update(value=self.uploaded_files)
        self.show_notification("File not found.")
        return gr.update(value=self.uploaded_files)

    def delete_all_files(self):
        self.uploaded_files.clear()
        self.show_notification("All files deleted.")
        return gr.update(value=[])

    def show_notification(self, message):
        if self.notification_box is not None:
            self.notification_box.value = message
            self.notification_box.visible = True
            self.notification_box.visible = False

    def create_interface(self):
        with gr.Blocks() as demo:
            with gr.Row():
                with gr.Column(scale=1):
                    # File Upload Section
                    file_input = gr.File(label="Upload File")
                    upload_btn = gr.Button("Upload")
                    
                    # File List and Deletion Section
                    file_list = gr.Textbox(label="Uploaded Files", interactive=False)
                    with gr.Row():
                        file_to_delete = gr.Textbox(label="File to Delete")
                        with gr.Column():
                            delete_btn = gr.Button("Delete File")
                            delete_all_btn = gr.Button("Delete All Files")
                    
                    # Notification Area
                    self.notification_box = gr.Textbox(label="Notifications", interactive=False, visible=False)

                    # File Upload Action
                    upload_btn.click(
                        fn=self.upload_file, 
                        inputs=file_input, 
                        outputs=file_list
                    )

                    # Single File Deletion Action
                    delete_btn.click(
                        fn=self.delete_file, 
                        inputs=file_to_delete, 
                        outputs=file_list
                    )

                    # Delete All Files Action
                    delete_all_btn.click(
                        fn=self.delete_all_files, 
                        outputs=file_list
                    )

                with gr.Column(scale=2):
                    # Chatbot Interface
                    chatbot = gr.Chatbot()
                    
                    # Input and Buttons Row
                    with gr.Row():
                        with gr.Column(scale=4):
                            msg = gr.Textbox(label="Message")
                        with gr.Column(scale=1):
                            submit_btn = gr.Button("Send")
                            clear_btn = gr.Button("Clear")

                    # Chatbot Message Submission
                    submit_btn.click(
                        fn=lambda message, chat_history: (message, chat_history + [[message, "I'm a placeholder chatbot response"]]),
                        inputs=[msg, chatbot],
                        outputs=[msg, chatbot]
                    )

                    # Clear Chat History
                    clear_btn.click(lambda: None, None, chatbot, queue=False)

        return demo

# Launch the interface
if __name__ == "__main__":
    interface = ChatbotInterface()
    demo = interface.create_interface()
    demo.launch()