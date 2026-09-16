


class Recall():

    def __init__(self):
        pass

    def calculate_IoU(self, source1, source2):
        """this function decides if the retrival is correct or not by calculating overlap"""
        
        source1_start = source1['first_character_index']
        source1_end = source1['last_character_index']

        source2_start = source2['first_character_index']
        source2_end = source2['last_character_index']

        # union = max(source2_end - source1_start, source1_end - source2_start)
        # intersection =  min(source1_end - source2_start, source2_end - source1_start)
        intersection = max(0, min(source1_end, source2_end) - max(source1_start, source2_start))
        union = max(source1_end, source2_end) - min(source1_start, source2_start)

        return intersection / union if union > 0 else 0

    
    def recall_calculation(self, reference, retrived):

        # recall = reference source found  / reference source number

        correct_retrived = 0
        for ref in reference:
            
            for ret in retrived:

                if ref['file_path'] != ret['file_path']:
                    continue
                if self.calculate_IoU(ref, ret) >= 0.05:
                    correct_retrived += 1
                    break



        return correct_retrived / len(reference)
    
        
