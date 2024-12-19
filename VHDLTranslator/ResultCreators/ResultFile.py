from io import TextIOWrapper
import os
import shutil
import traceback

class ResultFile:
    def _create_file(self, result_path: str) -> TextIOWrapper:
        try:
            if os.path.exists(result_path):
                # Construct the new name for the existing file
                base, ext = os.path.splitext(result_path)
                new_name = base + '_old' + ext
                
                # Rename the existing file
                shutil.move(result_path, new_name)

            # Create a new file
            return open(result_path, 'w')
            

        except Exception:
            print(traceback.format_exc())
            #print(traceback.exc_info()[2])

    def _is_nil(self, result: str) -> str:
        if result == "":
            return "Nil"
        else: return result
        