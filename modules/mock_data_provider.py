"""
Mock data provider for the Shopping Assistant application.

This module provides mock product data for testing purposes.
"""

import random
from datetime import datetime, timedelta

class MockDataProvider:
    """
    Provides mock product data for testing purposes.
    """
    
    def __init__(self):
        """Initialize the MockDataProvider."""
        self.laptop_data = self._generate_laptop_data()
        self.phone_data = self._generate_phone_data()
        self.headphone_data = self._generate_headphone_data()
        self.tv_data = self._generate_tv_data()
        self.fridge_data = self._generate_fridge_data()
        self.generic_data = self._generate_generic_data()
        
    def get_products(self, product_type, budget, preferences=None):
        """
        Get mock product data based on product type.
        
        Args:
            product_type: Type of product to get data for
            budget: Budget constraint
            preferences: List of preferences
            
        Returns:
            list: Mock product data
        """
        # Convert product type to lowercase for case-insensitive matching
        product_type_lower = product_type.lower()
        
        # Select appropriate data based on product type
        if 'laptop' in product_type_lower:
            products = self.laptop_data
        elif 'phone' in product_type_lower or 'mobile' in product_type_lower:
            products = self.phone_data
        elif 'headphone' in product_type_lower or 'earphone' in product_type_lower:
            products = self.headphone_data
        elif 'tv' in product_type_lower or 'television' in product_type_lower:
            products = self.tv_data
        elif 'fridge' in product_type_lower or 'refrigerator' in product_type_lower:
            products = self.fridge_data
        else:
            # Use generic data for other product types
            products = self.generic_data
            
        # Filter products by budget (allow 10% over budget)
        max_budget = budget * 1.1
        filtered_products = [p for p in products if p['price'] <= max_budget]
        
        # Filter by preferences if provided
        if preferences:
            preference_matched_products = []
            for product in filtered_products:
                # Check if any preference matches product name or features
                product_text = product['name'].lower() + ' ' + ' '.join(product['features']).lower()
                matches = []
                for preference in preferences:
                    if preference.lower() in product_text:
                        matches.append(preference)
                if matches:
                    product['matched_preferences'] = matches
                    preference_matched_products.append(product)
            
            # If we have products matching preferences, use those
            if preference_matched_products:
                filtered_products = preference_matched_products
                
        # Sort by rating (descending)
        filtered_products.sort(key=lambda p: (p.get('rating', 0), -p.get('price', 0)), reverse=True)
        
        return filtered_products
        
    def _generate_laptop_data(self):
        """Generate mock laptop data."""
        return [
            {
                'name': 'ASUS TUF Gaming F15 Core i5 10th Gen',
                'url': 'https://www.example.com/laptop1',
                'price': 49990,
                'price_text': '₹49,990',
                'rating': 4.3,
                'review_count': 1245,
                'features': [
                    '15.6 inch Full HD Display',
                    '8 GB RAM',
                    '512 GB SSD',
                    'Windows 11 Home',
                    'NVIDIA GeForce GTX 1650 4GB Graphics',
                    'Gaming Laptop'
                ],
                'image_url': 'https://www.example.com/images/laptop1.jpg',
                'platform': 'Flipkart'
            },
            {
                'name': 'Lenovo IdeaPad Gaming 3 Ryzen 5 Hexa Core 5600H',
                'url': 'https://www.example.com/laptop2',
                'price': 48990,
                'price_text': '₹48,990',
                'rating': 4.2,
                'review_count': 987,
                'features': [
                    '15.6 inch Full HD Display',
                    '8 GB RAM',
                    '512 GB SSD',
                    'Windows 11 Home',
                    'NVIDIA GeForce GTX 1650 4GB Graphics',
                    'Gaming Laptop'
                ],
                'image_url': 'https://www.example.com/images/laptop2.jpg',
                'platform': 'Flipkart'
            },
            {
                'name': 'HP Victus Core i5 11th Gen',
                'url': 'https://www.example.com/laptop3',
                'price': 51990,
                'price_text': '₹51,990',
                'rating': 4.1,
                'review_count': 856,
                'features': [
                    '16.1 inch Full HD Display',
                    '8 GB RAM',
                    '512 GB SSD',
                    'Windows 11 Home',
                    'NVIDIA GeForce GTX 1650 4GB Graphics',
                    'Gaming Laptop'
                ],
                'image_url': 'https://www.example.com/images/laptop3.jpg',
                'platform': 'Amazon'
            },
            {
                'name': 'Dell Inspiron 3511 Core i3 11th Gen',
                'url': 'https://www.example.com/laptop4',
                'price': 38990,
                'price_text': '₹38,990',
                'rating': 4.0,
                'review_count': 1123,
                'features': [
                    '15.6 inch Full HD Display',
                    '8 GB RAM',
                    '256 GB SSD',
                    'Windows 11 Home',
                    'Intel UHD Graphics',
                    'Thin and Light Laptop'
                ],
                'image_url': 'https://www.example.com/images/laptop4.jpg',
                'platform': 'Amazon'
            },
            {
                'name': 'Apple MacBook Air M1',
                'url': 'https://www.example.com/laptop5',
                'price': 89990,
                'price_text': '₹89,990',
                'rating': 4.8,
                'review_count': 2345,
                'features': [
                    '13.3 inch Retina Display',
                    '8 GB RAM',
                    '256 GB SSD',
                    'macOS',
                    'Apple M1 Chip',
                    'Thin and Light Laptop'
                ],
                'image_url': 'https://www.example.com/images/laptop5.jpg',
                'platform': 'Amazon'
            }
        ]
        
    def _generate_phone_data(self):
        """Generate mock phone data."""
        return [
            {
                'name': 'Samsung Galaxy S23 Ultra',
                'url': 'https://www.example.com/phone1',
                'price': 99999,
                'price_text': '₹99,999',
                'rating': 4.5,
                'review_count': 3456,
                'features': [
                    '6.8 inch Dynamic AMOLED Display',
                    '12 GB RAM',
                    '256 GB Storage',
                    '200MP + 12MP + 10MP + 10MP Quad Rear Camera',
                    '5000 mAh Battery',
                    '5G'
                ],
                'image_url': 'https://www.example.com/images/phone1.jpg',
                'platform': 'Amazon'
            },
            {
                'name': 'Apple iPhone 14 Pro',
                'url': 'https://www.example.com/phone2',
                'price': 119900,
                'price_text': '₹1,19,900',
                'rating': 4.7,
                'review_count': 2876,
                'features': [
                    '6.1 inch Super Retina XDR Display',
                    '6 GB RAM',
                    '128 GB Storage',
                    '48MP + 12MP + 12MP Triple Rear Camera',
                    'A16 Bionic Chip',
                    '5G'
                ],
                'image_url': 'https://www.example.com/images/phone2.jpg',
                'platform': 'Flipkart'
            },
            {
                'name': 'OnePlus 11 5G',
                'url': 'https://www.example.com/phone3',
                'price': 56999,
                'price_text': '₹56,999',
                'rating': 4.4,
                'review_count': 1987,
                'features': [
                    '6.7 inch Fluid AMOLED Display',
                    '16 GB RAM',
                    '256 GB Storage',
                    '50MP + 48MP + 32MP Triple Rear Camera',
                    '5000 mAh Battery',
                    '5G'
                ],
                'image_url': 'https://www.example.com/images/phone3.jpg',
                'platform': 'Amazon'
            },
            {
                'name': 'Xiaomi Redmi Note 12 Pro',
                'url': 'https://www.example.com/phone4',
                'price': 24999,
                'price_text': '₹24,999',
                'rating': 4.2,
                'review_count': 3456,
                'features': [
                    '6.67 inch Full HD+ AMOLED Display',
                    '8 GB RAM',
                    '128 GB Storage',
                    '50MP + 8MP + 2MP Triple Rear Camera',
                    '5000 mAh Battery',
                    '5G'
                ],
                'image_url': 'https://www.example.com/images/phone4.jpg',
                'platform': 'Flipkart'
            },
            {
                'name': 'Realme 10 Pro+',
                'url': 'https://www.example.com/phone5',
                'price': 19999,
                'price_text': '₹19,999',
                'rating': 4.1,
                'review_count': 2345,
                'features': [
                    '6.7 inch Full HD+ AMOLED Display',
                    '8 GB RAM',
                    '128 GB Storage',
                    '108MP + 8MP + 2MP Triple Rear Camera',
                    '5000 mAh Battery',
                    '5G'
                ],
                'image_url': 'https://www.example.com/images/phone5.jpg',
                'platform': 'Amazon'
            }
        ]
        
    def _generate_headphone_data(self):
        """Generate mock headphone data."""
        return [
            {
                'name': 'Sony WH-1000XM4 Wireless Noise Cancelling Headphones',
                'url': 'https://www.example.com/headphone1',
                'price': 19990,
                'price_text': '₹19,990',
                'rating': 4.6,
                'review_count': 3456,
                'features': [
                    'Industry Leading Noise Cancellation',
                    'Wireless Bluetooth',
                    '30 Hours Battery Life',
                    'Touch Controls',
                    'Built-in Microphone'
                ],
                'image_url': 'https://www.example.com/images/headphone1.jpg',
                'platform': 'Amazon'
            },
            {
                'name': 'Apple AirPods Pro (2nd Generation)',
                'url': 'https://www.example.com/headphone2',
                'price': 24990,
                'price_text': '₹24,990',
                'rating': 4.7,
                'review_count': 2876,
                'features': [
                    'Active Noise Cancellation',
                    'Wireless Bluetooth',
                    '6 Hours Battery Life',
                    'Spatial Audio',
                    'Water Resistant'
                ],
                'image_url': 'https://www.example.com/images/headphone2.jpg',
                'platform': 'Flipkart'
            },
            {
                'name': 'boAt Rockerz 450 Bluetooth Headphone',
                'url': 'https://www.example.com/headphone3',
                'price': 1499,
                'price_text': '₹1,499',
                'rating': 4.2,
                'review_count': 5678,
                'features': [
                    'Wireless Bluetooth',
                    '15 Hours Battery Life',
                    'Padded Ear Cushions',
                    'Built-in Microphone',
                    'Foldable Design'
                ],
                'image_url': 'https://www.example.com/images/headphone3.jpg',
                'platform': 'Amazon'
            },
            {
                'name': 'JBL Tune 760NC Wireless Headphones',
                'url': 'https://www.example.com/headphone4',
                'price': 5999,
                'price_text': '₹5,999',
                'rating': 4.3,
                'review_count': 1234,
                'features': [
                    'Active Noise Cancellation',
                    'Wireless Bluetooth',
                    '35 Hours Battery Life',
                    'Voice Assistant Support',
                    'Foldable Design'
                ],
                'image_url': 'https://www.example.com/images/headphone4.jpg',
                'platform': 'Flipkart'
            },
            {
                'name': 'Sennheiser HD 458BT Wireless Headphones',
                'url': 'https://www.example.com/headphone5',
                'price': 9990,
                'price_text': '₹9,990',
                'rating': 4.4,
                'review_count': 876,
                'features': [
                    'Active Noise Cancellation',
                    'Wireless Bluetooth',
                    '30 Hours Battery Life',
                    'Voice Assistant Support',
                    'Foldable Design'
                ],
                'image_url': 'https://www.example.com/images/headphone5.jpg',
                'platform': 'Amazon'
            }
        ]
        
    def _generate_tv_data(self):
        """Generate mock TV data."""
        return [
            {
                'name': 'Samsung Crystal 4K Ultra HD Smart LED TV UA55AUE60AKLXL',
                'url': 'https://www.example.com/tv1',
                'price': 49990,
                'price_text': '₹49,990',
                'rating': 4.4,
                'review_count': 2345,
                'features': [
                    '55 inch 4K Ultra HD Display',
                    'Smart TV with Tizen OS',
                    'Crystal Processor 4K',
                    '3 HDMI Ports',
                    'Built-in Wi-Fi'
                ],
                'image_url': 'https://www.example.com/images/tv1.jpg',
                'platform': 'Amazon'
            },
            {
                'name': 'LG 43 inches 4K Ultra HD Smart LED TV 43UQ7500PSF',
                'url': 'https://www.example.com/tv2',
                'price': 32990,
                'price_text': '₹32,990',
                'rating': 4.3,
                'review_count': 1876,
                'features': [
                    '43 inch 4K Ultra HD Display',
                    'Smart TV with webOS',
                    'AI ThinQ',
                    '3 HDMI Ports',
                    'Built-in Wi-Fi'
                ],
                'image_url': 'https://www.example.com/images/tv2.jpg',
                'platform': 'Flipkart'
            },
            {
                'name': 'Sony Bravia 4K Ultra HD Smart LED Google TV KD-55X74K',
                'url': 'https://www.example.com/tv3',
                'price': 59990,
                'price_text': '₹59,990',
                'rating': 4.5,
                'review_count': 1234,
                'features': [
                    '55 inch 4K Ultra HD Display',
                    'Smart TV with Google TV',
                    '4K HDR Processor X1',
                    '3 HDMI Ports',
                    'Built-in Wi-Fi'
                ],
                'image_url': 'https://www.example.com/images/tv3.jpg',
                'platform': 'Amazon'
            },
            {
                'name': 'Mi 43 inches 4K Ultra HD Smart Android LED TV X Series L43M7-A2IN',
                'url': 'https://www.example.com/tv4',
                'price': 25999,
                'price_text': '₹25,999',
                'rating': 4.2,
                'review_count': 3456,
                'features': [
                    '43 inch 4K Ultra HD Display',
                    'Smart TV with Android TV',
                    'PatchWall 4',
                    '3 HDMI Ports',
                    'Built-in Wi-Fi'
                ],
                'image_url': 'https://www.example.com/images/tv4.jpg',
                'platform': 'Flipkart'
            },
            {
                'name': 'TCL 50 inches 4K Ultra HD Smart QLED Google TV 50C635',
                'url': 'https://www.example.com/tv5',
                'price': 39990,
                'price_text': '₹39,990',
                'rating': 4.1,
                'review_count': 876,
                'features': [
                    '50 inch 4K Ultra HD QLED Display',
                    'Smart TV with Google TV',
                    'MEMC Technology',
                    '3 HDMI Ports',
                    'Built-in Wi-Fi'
                ],
                'image_url': 'https://www.example.com/images/tv5.jpg',
                'platform': 'Amazon'
            }
        ]
        
    def _generate_fridge_data(self):
        """Generate mock fridge data."""
        return [
            {
                'name': 'Samsung 253 L 3 Star Double Door Refrigerator RT28T3122S8/HL',
                'url': 'https://www.example.com/fridge1',
                'price': 25990,
                'price_text': '₹25,990',
                'rating': 4.3,
                'review_count': 1234,
                'features': [
                    '253 L Capacity',
                    'Double Door',
                    'Frost Free',
                    'Digital Inverter Compressor',
                    'Energy Efficient'
                ],
                'image_url': 'https://www.example.com/images/fridge1.jpg',
                'platform': 'Amazon'
            },
            {
                'name': 'LG 260 L 3 Star Frost-Free Double Door Refrigerator GL-I292RPZL',
                'url': 'https://www.example.com/fridge2',
                'price': 26990,
                'price_text': '₹26,990',
                'rating': 4.4,
                'review_count': 987,
                'features': [
                    '260 L Capacity',
                    'Double Door',
                    'Frost Free',
                    'Smart Inverter Compressor',
                    'Energy Efficient'
                ],
                'image_url': 'https://www.example.com/images/fridge2.jpg',
                'platform': 'Flipkart'
            },
            {
                'name': 'Whirlpool 200 L 4 Star Single Door Refrigerator 215 IMPRO ROY 4S',
                'url': 'https://www.example.com/fridge3',
                'price': 16990,
                'price_text': '₹16,990',
                'rating': 4.2,
                'review_count': 876,
                'features': [
                    '200 L Capacity',
                    'Single Door',
                    'Direct Cool',
                    'Intellisense Inverter Technology',
                    'Energy Efficient'
                ],
                'image_url': 'https://www.example.com/images/fridge3.jpg',
                'platform': 'Amazon'
            },
            {
                'name': 'Godrej 564 L Frost Free Side-By-Side Refrigerator RS EONVELVET 579 RFD',
                'url': 'https://www.example.com/fridge4',
                'price': 69990,
                'price_text': '₹69,990',
                'rating': 4.5,
                'review_count': 567,
                'features': [
                    '564 L Capacity',
                    'Side-By-Side Door',
                    'Frost Free',
                    'Intelligent Inverter Compressor',
                    'Energy Efficient'
                ],
                'image_url': 'https://www.example.com/images/fridge4.jpg',
                'platform': 'Flipkart'
            },
            {
                'name': 'Haier 195 L 4 Star Direct-Cool Single Door Refrigerator HED-20CFDS',
                'url': 'https://www.example.com/fridge5',
                'price': 14990,
                'price_text': '₹14,990',
                'rating': 4.1,
                'review_count': 765,
                'features': [
                    '195 L Capacity',
                    'Single Door',
                    'Direct Cool',
                    '1 Hour Icing Technology',
                    'Energy Efficient'
                ],
                'image_url': 'https://www.example.com/images/fridge5.jpg',
                'platform': 'Amazon'
            }
        ]
        
    def _generate_generic_data(self):
        """Generate mock generic product data."""
        return [
            {
                'name': 'Generic Product 1',
                'url': 'https://www.example.com/product1',
                'price': 9999,
                'price_text': '₹9,999',
                'rating': 4.2,
                'review_count': 876,
                'features': [
                    'Feature 1',
                    'Feature 2',
                    'Feature 3',
                    'Feature 4',
                    'Feature 5'
                ],
                'image_url': 'https://www.example.com/images/product1.jpg',
                'platform': 'Amazon'
            },
            {
                'name': 'Generic Product 2',
                'url': 'https://www.example.com/product2',
                'price': 19999,
                'price_text': '₹19,999',
                'rating': 4.3,
                'review_count': 765,
                'features': [
                    'Feature 1',
                    'Feature 2',
                    'Feature 3',
                    'Feature 4',
                    'Feature 5'
                ],
                'image_url': 'https://www.example.com/images/product2.jpg',
                'platform': 'Flipkart'
            },
            {
                'name': 'Generic Product 3',
                'url': 'https://www.example.com/product3',
                'price': 29999,
                'price_text': '₹29,999',
                'rating': 4.4,
                'review_count': 654,
                'features': [
                    'Feature 1',
                    'Feature 2',
                    'Feature 3',
                    'Feature 4',
                    'Feature 5'
                ],
                'image_url': 'https://www.example.com/images/product3.jpg',
                'platform': 'Amazon'
            },
            {
                'name': 'Generic Product 4',
                'url': 'https://www.example.com/product4',
                'price': 39999,
                'price_text': '₹39,999',
                'rating': 4.5,
                'review_count': 543,
                'features': [
                    'Feature 1',
                    'Feature 2',
                    'Feature 3',
                    'Feature 4',
                    'Feature 5'
                ],
                'image_url': 'https://www.example.com/images/product4.jpg',
                'platform': 'Flipkart'
            },
            {
                'name': 'Generic Product 5',
                'url': 'https://www.example.com/product5',
                'price': 49999,
                'price_text': '₹49,999',
                'rating': 4.6,
                'review_count': 432,
                'features': [
                    'Feature 1',
                    'Feature 2',
                    'Feature 3',
                    'Feature 4',
                    'Feature 5'
                ],
                'image_url': 'https://www.example.com/images/product5.jpg',
                'platform': 'Amazon'
            }
        ]
