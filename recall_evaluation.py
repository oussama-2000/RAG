


class Recall():

    def __init__(self):
        pass

    def calculate_IoU(self, source1, source2):
        source1_start = source1['start_index_character']
        source1_end = source1['end_index_character']

        source2_start = source2['start_index_character']
        source2_end = source2['end_index_character']

        intersection = source1_start + source2_end
        union = source2_start - source1_end

        return intersection / union

    

