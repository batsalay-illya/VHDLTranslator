import os
import shutil
import traceback

class FileCreator:
    def _create_file(self, result_path : str, result_data : str):
        try:
            if os.path.exists(result_path):
                # Construct the new name for the existing file
                base, ext = os.path.splitext(result_path)
                new_name = base + '_old' + ext
                
                # Rename the existing file
                shutil.move(result_path, new_name)

            # Create a new file and write data to it
            with open(result_path, 'w') as file:
                file.write(result_data)

        except Exception:
            print(traceback.format_exc())
            #print(traceback.exc_info()[2])
        